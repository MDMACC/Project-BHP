const mongoose = require('mongoose');

const shopSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    default: 'Bluez PowerHouse'
  },
  address: {
    street: {
      type: String,
      required: true,
      default: '250 W Spazier Ave 101'
    },
    city: {
      type: String,
      required: true,
      default: 'Burbank'
    },
    state: {
      type: String,
      required: true,
      default: 'CA'
    },
    zipCode: {
      type: String,
      required: true,
      default: '91502'
    },
    country: {
      type: String,
      default: 'USA'
    }
  },
  contactInfo: {
    phone: String,
    email: String,
    website: String
  },
  businessInfo: {
    taxId: String,
    licenseNumber: String,
    businessHours: {
      monday: { open: String, close: String },
      tuesday: { open: String, close: String },
      wednesday: { open: String, close: String },
      thursday: { open: String, close: String },
      friday: { open: String, close: String },
      saturday: { open: String, close: String },
      sunday: { open: String, close: String }
    }
  },
  settings: {
    timezone: {
      type: String,
      default: 'America/Los_Angeles'
    },
    currency: {
      type: String,
      default: 'USD'
    },
    defaultOrderTimeLimit: {
      type: Number,
      default: 72 // hours
    }
  }
}, {
  timestamps: true
});

// Virtual for full address
shopSchema.virtual('fullAddress').get(function() {
  const addr = this.address;
  return `${addr.street}, ${addr.city}, ${addr.state} ${addr.zipCode}`;
});

// Ensure only one shop document exists
shopSchema.statics.getShopInfo = async function() {
  let shop = await this.findOne();
  if (!shop) {
    shop = new this();
    await shop.save();
  }
  return shop;
};

module.exports = mongoose.model('Shop', shopSchema);
