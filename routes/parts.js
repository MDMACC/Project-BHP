const express = require('express');
const { body, validationResult, query } = require('express-validator');
const Part = require('../models/Part');
const Contact = require('../models/Contact');
const { auth, adminAuth } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/parts
// @desc    Get all parts with filtering and pagination
// @access  Private
router.get('/', auth, [
  query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
  query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
  query('category').optional().isString(),
  query('brand').optional().isString(),
  query('search').optional().isString()
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
    const filter = { isActive: true };
    
    if (req.query.category) {
      filter.category = req.query.category;
    }
    
    if (req.query.brand) {
      filter.brand = new RegExp(req.query.brand, 'i');
    }
    
    if (req.query.search) {
      filter.$or = [
        { name: new RegExp(req.query.search, 'i') },
        { partNumber: new RegExp(req.query.search, 'i') },
        { description: new RegExp(req.query.search, 'i') }
      ];
    }

    const parts = await Part.find(filter)
      .populate('supplier', 'name company contactInfo.email contactInfo.phone')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);

    const total = await Part.countDocuments(filter);

    res.json({
      parts,
      pagination: {
        current: page,
        pages: Math.ceil(total / limit),
        total,
        hasNext: page < Math.ceil(total / limit),
        hasPrev: page > 1
      }
    });
  } catch (error) {
    console.error('Get parts error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/parts/:id
// @desc    Get single part
// @access  Private
router.get('/:id', auth, async (req, res) => {
  try {
    const part = await Part.findById(req.params.id)
      .populate('supplier', 'name company contactInfo.email contactInfo.phone specialties');

    if (!part) {
      return res.status(404).json({ message: 'Part not found' });
    }

    res.json(part);
  } catch (error) {
    console.error('Get part error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/parts
// @desc    Create new part
// @access  Private (Admin/Manager)
router.post('/', adminAuth, [
  body('partNumber').notEmpty().withMessage('Part number is required'),
  body('name').notEmpty().withMessage('Part name is required'),
  body('category').isIn(['engine', 'brake', 'transmission', 'electrical', 'body', 'interior', 'exhaust', 'suspension', 'other']).withMessage('Invalid category'),
  body('brand').notEmpty().withMessage('Brand is required'),
  body('price').isFloat({ min: 0 }).withMessage('Price must be a positive number'),
  body('cost').isFloat({ min: 0 }).withMessage('Cost must be a positive number'),
  body('supplier').isMongoId().withMessage('Valid supplier ID is required'),
  body('quantityInStock').isInt({ min: 0 }).withMessage('Quantity must be a non-negative integer')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Check if part number already exists
    const existingPart = await Part.findOne({ partNumber: req.body.partNumber.toUpperCase() });
    if (existingPart) {
      return res.status(400).json({ message: 'Part number already exists' });
    }

    // Verify supplier exists
    const supplier = await Contact.findById(req.body.supplier);
    if (!supplier) {
      return res.status(400).json({ message: 'Supplier not found' });
    }

    const part = new Part({
      ...req.body,
      partNumber: req.body.partNumber.toUpperCase()
    });

    await part.save();
    await part.populate('supplier', 'name company contactInfo.email contactInfo.phone');

    res.status(201).json(part);
  } catch (error) {
    console.error('Create part error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   PUT /api/parts/:id
// @desc    Update part
// @access  Private (Admin/Manager)
router.put('/:id', adminAuth, [
  body('name').optional().notEmpty().withMessage('Part name cannot be empty'),
  body('category').optional().isIn(['engine', 'brake', 'transmission', 'electrical', 'body', 'interior', 'exhaust', 'suspension', 'other']).withMessage('Invalid category'),
  body('price').optional().isFloat({ min: 0 }).withMessage('Price must be a positive number'),
  body('cost').optional().isFloat({ min: 0 }).withMessage('Cost must be a positive number'),
  body('quantityInStock').optional().isInt({ min: 0 }).withMessage('Quantity must be a non-negative integer')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const part = await Part.findById(req.params.id);
    if (!part) {
      return res.status(404).json({ message: 'Part not found' });
    }

    // If part number is being changed, check for duplicates
    if (req.body.partNumber && req.body.partNumber !== part.partNumber) {
      const existingPart = await Part.findOne({ partNumber: req.body.partNumber.toUpperCase() });
      if (existingPart) {
        return res.status(400).json({ message: 'Part number already exists' });
      }
      req.body.partNumber = req.body.partNumber.toUpperCase();
    }

    // If supplier is being changed, verify it exists
    if (req.body.supplier) {
      const supplier = await Contact.findById(req.body.supplier);
      if (!supplier) {
        return res.status(400).json({ message: 'Supplier not found' });
      }
    }

    Object.assign(part, req.body);
    await part.save();
    await part.populate('supplier', 'name company contactInfo.email contactInfo.phone');

    res.json(part);
  } catch (error) {
    console.error('Update part error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   DELETE /api/parts/:id
// @desc    Delete part (soft delete)
// @access  Private (Admin/Manager)
router.delete('/:id', adminAuth, async (req, res) => {
  try {
    const part = await Part.findById(req.params.id);
    if (!part) {
      return res.status(404).json({ message: 'Part not found' });
    }

    part.isActive = false;
    await part.save();

    res.json({ message: 'Part deleted successfully' });
  } catch (error) {
    console.error('Delete part error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/parts/low-stock
// @desc    Get parts with low stock
// @access  Private
router.get('/inventory/low-stock', auth, async (req, res) => {
  try {
    const parts = await Part.find({
      isActive: true,
      $expr: { $lte: ['$quantityInStock', '$minimumStockLevel'] }
    })
    .populate('supplier', 'name company contactInfo.email contactInfo.phone')
    .sort({ quantityInStock: 1 });

    res.json(parts);
  } catch (error) {
    console.error('Get low stock parts error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/parts/:id/restock
// @desc    Restock a part
// @access  Private (Admin/Manager)
router.post('/:id/restock', adminAuth, [
  body('quantity').isInt({ min: 1 }).withMessage('Quantity must be a positive integer')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const part = await Part.findById(req.params.id);
    if (!part) {
      return res.status(404).json({ message: 'Part not found' });
    }

    part.quantityInStock += req.body.quantity;
    part.lastRestocked = new Date();
    await part.save();

    res.json(part);
  } catch (error) {
    console.error('Restock part error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
