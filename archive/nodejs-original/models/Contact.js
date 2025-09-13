const mongoose = require('mongoose');

const contactSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  company: {
    type: String,
    trim: true
  },
  type: {
    type: String,
    enum: ['supplier', 'customer', 'vendor', 'distributor'],
    required: true
  },
  contactInfo: {
    email: {
      type: String,
      trim: true,
      lowercase: true
    },
    phone: {
      type: String,
      trim: true
    },
    mobile: {
      type: String,
      trim: true
    },
    fax: {
      type: String,
      trim: true
    }
  },
  address: {
    street: String,
    city: String,
    state: String,
    zipCode: String,
    country: {
      type: String,
      default: 'USA'
    }
  },
  businessInfo: {
    taxId: String,
    licenseNumber: String,
    website: String,
    creditLimit: {
      type: Number,
      default: 0
    },
    paymentTerms: {
      type: String,
      enum: ['net_15', 'net_30', 'net_45', 'net_60', 'cash_on_delivery', 'prepaid'],
      default: 'net_30'
    }
  },
  specialties: [String], // What types of parts they specialize in
  rating: {
    type: Number,
    min: 1,
    max: 5,
    default: 3
  },
  notes: String,
  isActive: {
    type: Boolean,
    default: true
  },
  lastContactDate: {
    type: Date
  }
}, {
  timestamps: true
});

// Index for better search performance
contactSchema.index({ name: 'text', company: 'text' });
contactSchema.index({ type: 1 });
contactSchema.index({ 'contactInfo.email': 1 });

// Virtual for full address
contactSchema.virtual('fullAddress').get(function() {
  const addr = this.address;
  if (!addr) return '';
  
  const parts = [addr.street, addr.city, addr.state, addr.zipCode].filter(Boolean);
  return parts.join(', ');
});

// Virtual for primary contact method
contactSchema.virtual('primaryContact').get(function() {
  const contact = this.contactInfo;
  return contact.mobile || contact.phone || contact.email || 'No contact info';
});

module.exports = mongoose.model('Contact', contactSchema);
