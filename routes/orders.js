const express = require('express');
const { body, validationResult, query } = require('express-validator');
const Order = require('../models/Order');
const Part = require('../models/Part');
const Contact = require('../models/Contact');
const { auth, adminAuth } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/orders
// @desc    Get all orders with filtering and pagination
// @access  Private
router.get('/', auth, [
  query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
  query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
  query('status').optional().isIn(['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']),
  query('supplier').optional().isMongoId()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const skip = (page - 1) * limit;

    // Build filter object
    const filter = {};
    
    if (req.query.status) {
      filter.status = req.query.status;
    }
    
    if (req.query.supplier) {
      filter.supplier = req.query.supplier;
    }

    const orders = await Order.find(filter)
      .populate('supplier', 'name company contactInfo.email contactInfo.phone')
      .populate('parts.part', 'partNumber name brand price')
      .populate('createdBy', 'username')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);

    const total = await Order.countDocuments(filter);

    res.json({
      orders,
      pagination: {
        current: page,
        pages: Math.ceil(total / limit),
        total,
        hasNext: page < Math.ceil(total / limit),
        hasPrev: page > 1
      }
    });
  } catch (error) {
    console.error('Get orders error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/orders/:id
// @desc    Get single order
// @access  Private
router.get('/:id', auth, async (req, res) => {
  try {
    const order = await Order.findById(req.params.id)
      .populate('supplier', 'name company contactInfo.email contactInfo.phone address')
      .populate('parts.part', 'partNumber name brand price cost')
      .populate('createdBy', 'username email');

    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }

    res.json(order);
  } catch (error) {
    console.error('Get order error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/orders
// @desc    Create new order
// @access  Private (Admin/Manager)
router.post('/', adminAuth, [
  body('supplier').isMongoId().withMessage('Valid supplier ID is required'),
  body('parts').isArray({ min: 1 }).withMessage('At least one part is required'),
  body('parts.*.part').isMongoId().withMessage('Valid part ID is required'),
  body('parts.*.quantity').isInt({ min: 1 }).withMessage('Quantity must be a positive integer'),
  body('parts.*.unitPrice').isFloat({ min: 0 }).withMessage('Unit price must be a positive number'),
  body('customTimeLimit').optional().isInt({ min: 1, max: 168 }).withMessage('Time limit must be between 1 and 168 hours')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Verify supplier exists
    const supplier = await Contact.findById(req.body.supplier);
    if (!supplier) {
      return res.status(400).json({ message: 'Supplier not found' });
    }

    // Verify all parts exist and calculate totals
    const parts = [];
    let totalAmount = 0;

    for (const orderPart of req.body.parts) {
      const part = await Part.findById(orderPart.part);
      if (!part) {
        return res.status(400).json({ message: `Part with ID ${orderPart.part} not found` });
      }

      const totalPrice = orderPart.quantity * orderPart.unitPrice;
      totalAmount += totalPrice;

      parts.push({
        part: part._id,
        quantity: orderPart.quantity,
        unitPrice: orderPart.unitPrice,
        totalPrice: totalPrice
      });
    }

    const order = new Order({
      supplier: req.body.supplier,
      parts: parts,
      totalAmount: totalAmount,
      customTimeLimit: req.body.customTimeLimit || 72,
      expectedDeliveryDate: req.body.expectedDeliveryDate,
      notes: req.body.notes,
      createdBy: req.user._id
    });

    await order.save();
    await order.populate('supplier', 'name company contactInfo.email contactInfo.phone');
    await order.populate('parts.part', 'partNumber name brand');

    res.status(201).json(order);
  } catch (error) {
    console.error('Create order error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   PUT /api/orders/:id
// @desc    Update order
// @access  Private (Admin/Manager)
router.put('/:id', adminAuth, [
  body('status').optional().isIn(['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']).withMessage('Invalid status'),
  body('customTimeLimit').optional().isInt({ min: 1, max: 168 }).withMessage('Time limit must be between 1 and 168 hours')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const order = await Order.findById(req.params.id);
    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }

    // Update countdown if custom time limit is changed
    if (req.body.customTimeLimit && req.body.customTimeLimit !== order.customTimeLimit) {
      order.customTimeLimit = req.body.customTimeLimit;
      order.countdownEndTime = new Date(Date.now() + (req.body.customTimeLimit * 60 * 60 * 1000));
    }

    // Update shipping info if provided
    if (req.body.shippingInfo) {
      order.shippingInfo = { ...order.shippingInfo, ...req.body.shippingInfo };
    }

    // Update other fields
    Object.assign(order, req.body);
    await order.save();

    await order.populate('supplier', 'name company contactInfo.email contactInfo.phone');
    await order.populate('parts.part', 'partNumber name brand');

    res.json(order);
  } catch (error) {
    console.error('Update order error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   DELETE /api/orders/:id
// @desc    Cancel order
// @access  Private (Admin/Manager)
router.delete('/:id', adminAuth, async (req, res) => {
  try {
    const order = await Order.findById(req.params.id);
    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }

    if (order.status === 'delivered') {
      return res.status(400).json({ message: 'Cannot cancel delivered order' });
    }

    order.status = 'cancelled';
    await order.save();

    res.json({ message: 'Order cancelled successfully' });
  } catch (error) {
    console.error('Cancel order error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/orders/shipping/overdue
// @desc    Get overdue orders
// @access  Private
router.get('/shipping/overdue', auth, async (req, res) => {
  try {
    const now = new Date();
    const orders = await Order.find({
      status: { $in: ['confirmed', 'shipped'] },
      countdownEndTime: { $lt: now }
    })
    .populate('supplier', 'name company contactInfo.email contactInfo.phone')
    .populate('parts.part', 'partNumber name')
    .sort({ countdownEndTime: 1 });

    res.json(orders);
  } catch (error) {
    console.error('Get overdue orders error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/orders/shipping/urgent
// @desc    Get urgent orders (less than 24 hours remaining)
// @access  Private
router.get('/shipping/urgent', auth, async (req, res) => {
  try {
    const now = new Date();
    const twentyFourHours = new Date(now.getTime() + (24 * 60 * 60 * 1000));
    
    const orders = await Order.find({
      status: { $in: ['confirmed', 'shipped'] },
      countdownEndTime: { $gt: now, $lt: twentyFourHours }
    })
    .populate('supplier', 'name company contactInfo.email contactInfo.phone')
    .populate('parts.part', 'partNumber name')
    .sort({ countdownEndTime: 1 });

    res.json(orders);
  } catch (error) {
    console.error('Get urgent orders error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/orders/:id/receive
// @desc    Mark order as received and update inventory
// @access  Private (Admin/Manager)
router.post('/:id/receive', adminAuth, async (req, res) => {
  try {
    const order = await Order.findById(req.params.id)
      .populate('parts.part');

    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }

    if (order.status === 'delivered') {
      return res.status(400).json({ message: 'Order already marked as delivered' });
    }

    // Update inventory for each part
    for (const orderPart of order.parts) {
      const part = orderPart.part;
      part.quantityInStock += orderPart.quantity;
      part.lastRestocked = new Date();
      await part.save();
    }

    // Update order status
    order.status = 'delivered';
    order.actualDeliveryDate = new Date();
    await order.save();

    await order.populate('supplier', 'name company contactInfo.email contactInfo.phone');
    await order.populate('parts.part', 'partNumber name brand');

    res.json(order);
  } catch (error) {
    console.error('Receive order error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
