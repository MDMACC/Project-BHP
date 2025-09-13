const express = require('express');
const { body, validationResult, query } = require('express-validator');
const Contact = require('../models/Contact');
const { auth, adminAuth } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/contacts
// @desc    Get all contacts with filtering and pagination
// @access  Private
router.get('/', auth, [
  query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
  query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
  query('type').optional().isIn(['supplier', 'customer', 'vendor', 'distributor']),
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
    
    if (req.query.type) {
      filter.type = req.query.type;
    }
    
    if (req.query.search) {
      filter.$or = [
        { name: new RegExp(req.query.search, 'i') },
        { company: new RegExp(req.query.search, 'i') },
        { 'contactInfo.email': new RegExp(req.query.search, 'i') }
      ];
    }

    const contacts = await Contact.find(filter)
      .sort({ name: 1 })
      .skip(skip)
      .limit(limit);

    const total = await Contact.countDocuments(filter);

    res.json({
      contacts,
      pagination: {
        current: page,
        pages: Math.ceil(total / limit),
        total,
        hasNext: page < Math.ceil(total / limit),
        hasPrev: page > 1
      }
    });
  } catch (error) {
    console.error('Get contacts error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/contacts/:id
// @desc    Get single contact
// @access  Private
router.get('/:id', auth, async (req, res) => {
  try {
    const contact = await Contact.findById(req.params.id);

    if (!contact) {
      return res.status(404).json({ message: 'Contact not found' });
    }

    res.json(contact);
  } catch (error) {
    console.error('Get contact error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/contacts
// @desc    Create new contact
// @access  Private (Admin/Manager)
router.post('/', adminAuth, [
  body('name').notEmpty().withMessage('Name is required'),
  body('type').isIn(['supplier', 'customer', 'vendor', 'distributor']).withMessage('Invalid contact type'),
  body('contactInfo.email').optional().isEmail().withMessage('Please include a valid email'),
  body('contactInfo.phone').optional().isString(),
  body('businessInfo.creditLimit').optional().isFloat({ min: 0 }).withMessage('Credit limit must be a positive number'),
  body('businessInfo.paymentTerms').optional().isIn(['net_15', 'net_30', 'net_45', 'net_60', 'cash_on_delivery', 'prepaid']).withMessage('Invalid payment terms')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const contact = new Contact(req.body);
    await contact.save();

    res.status(201).json(contact);
  } catch (error) {
    console.error('Create contact error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   PUT /api/contacts/:id
// @desc    Update contact
// @access  Private (Admin/Manager)
router.put('/:id', adminAuth, [
  body('name').optional().notEmpty().withMessage('Name cannot be empty'),
  body('type').optional().isIn(['supplier', 'customer', 'vendor', 'distributor']).withMessage('Invalid contact type'),
  body('contactInfo.email').optional().isEmail().withMessage('Please include a valid email'),
  body('businessInfo.creditLimit').optional().isFloat({ min: 0 }).withMessage('Credit limit must be a positive number'),
  body('businessInfo.paymentTerms').optional().isIn(['net_15', 'net_30', 'net_45', 'net_60', 'cash_on_delivery', 'prepaid']).withMessage('Invalid payment terms')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const contact = await Contact.findById(req.params.id);
    if (!contact) {
      return res.status(404).json({ message: 'Contact not found' });
    }

    Object.assign(contact, req.body);
    await contact.save();

    res.json(contact);
  } catch (error) {
    console.error('Update contact error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   DELETE /api/contacts/:id
// @desc    Delete contact (soft delete)
// @access  Private (Admin/Manager)
router.delete('/:id', adminAuth, async (req, res) => {
  try {
    const contact = await Contact.findById(req.params.id);
    if (!contact) {
      return res.status(404).json({ message: 'Contact not found' });
    }

    contact.isActive = false;
    await contact.save();

    res.json({ message: 'Contact deleted successfully' });
  } catch (error) {
    console.error('Delete contact error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/contacts/suppliers
// @desc    Get all suppliers
// @access  Private
router.get('/type/suppliers', auth, async (req, res) => {
  try {
    const suppliers = await Contact.find({
      type: 'supplier',
      isActive: true
    })
    .select('name company contactInfo specialties rating')
    .sort({ name: 1 });

    res.json(suppliers);
  } catch (error) {
    console.error('Get suppliers error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/contacts/customers
// @desc    Get all customers
// @access  Private
router.get('/type/customers', auth, async (req, res) => {
  try {
    const customers = await Contact.find({
      type: 'customer',
      isActive: true
    })
    .select('name company contactInfo address')
    .sort({ name: 1 });

    res.json(customers);
  } catch (error) {
    console.error('Get customers error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/contacts/:id/rate
// @desc    Rate a contact
// @access  Private
router.post('/:id/rate', auth, [
  body('rating').isInt({ min: 1, max: 5 }).withMessage('Rating must be between 1 and 5')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const contact = await Contact.findById(req.params.id);
    if (!contact) {
      return res.status(404).json({ message: 'Contact not found' });
    }

    contact.rating = req.body.rating;
    contact.lastContactDate = new Date();
    await contact.save();

    res.json(contact);
  } catch (error) {
    console.error('Rate contact error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
