const express = require('express');
const { body, validationResult } = require('express-validator');
const Shop = require('../models/Shop');
const { auth, adminAuth } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/shop
// @desc    Get shop information
// @access  Private
router.get('/', auth, async (req, res) => {
  try {
    const shop = await Shop.getShopInfo();
    res.json(shop);
  } catch (error) {
    console.error('Get shop info error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   PUT /api/shop
// @desc    Update shop information
// @access  Private (Admin/Manager)
router.put('/', adminAuth, [
  body('name').optional().notEmpty().withMessage('Shop name cannot be empty'),
  body('address.street').optional().notEmpty().withMessage('Street address cannot be empty'),
  body('address.city').optional().notEmpty().withMessage('City cannot be empty'),
  body('address.state').optional().notEmpty().withMessage('State cannot be empty'),
  body('address.zipCode').optional().notEmpty().withMessage('Zip code cannot be empty'),
  body('contactInfo.email').optional().isEmail().withMessage('Please include a valid email'),
  body('contactInfo.phone').optional().isString(),
  body('settings.timezone').optional().isString(),
  body('settings.currency').optional().isString(),
  body('settings.defaultOrderTimeLimit').optional().isInt({ min: 1, max: 168 }).withMessage('Time limit must be between 1 and 168 hours')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    let shop = await Shop.findOne();
    if (!shop) {
      shop = new Shop();
    }

    Object.assign(shop, req.body);
    await shop.save();

    res.json(shop);
  } catch (error) {
    console.error('Update shop info error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
