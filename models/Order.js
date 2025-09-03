const mongoose = require('mongoose');

const orderSchema = new mongoose.Schema({
  orderNumber: {
    type: String,
    required: true,
    unique: true
  },
  supplier: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Contact',
    required: true
  },
  parts: [{
    part: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Part',
      required: true
    },
    quantity: {
      type: Number,
      required: true,
      min: 1
    },
    unitPrice: {
      type: Number,
      required: true,
      min: 0
    },
    totalPrice: {
      type: Number,
      required: true,
      min: 0
    }
  }],
  totalAmount: {
    type: Number,
    required: true,
    min: 0
  },
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'],
    default: 'pending'
  },
  orderDate: {
    type: Date,
    default: Date.now
  },
  expectedDeliveryDate: {
    type: Date
  },
  actualDeliveryDate: {
    type: Date
  },
  shippingInfo: {
    trackingNumber: String,
    carrier: String,
    shippingMethod: String,
    shippingCost: {
      type: Number,
      default: 0
    }
  },
  customTimeLimit: {
    type: Number, // in hours
    default: 72 // 3 days default
  },
  countdownEndTime: {
    type: Date
  },
  notes: String,
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  }
}, {
  timestamps: true
});

// Pre-save middleware to generate order number and set countdown
orderSchema.pre('save', function(next) {
  if (this.isNew) {
    // Generate order number
    const timestamp = Date.now().toString().slice(-6);
    this.orderNumber = `ORD-${timestamp}`;
    
    // Set countdown end time if custom time limit is provided
    if (this.customTimeLimit) {
      this.countdownEndTime = new Date(Date.now() + (this.customTimeLimit * 60 * 60 * 1000));
    }
  }
  next();
});

// Virtual for countdown status
orderSchema.virtual('countdownStatus').get(function() {
  if (!this.countdownEndTime) return null;
  
  const now = new Date();
  const timeLeft = this.countdownEndTime - now;
  
  if (timeLeft <= 0) {
    return {
      status: 'overdue',
      timeLeft: 0,
      message: 'Package is overdue'
    };
  }
  
  const hours = Math.floor(timeLeft / (1000 * 60 * 60));
  const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
  
  return {
    status: hours < 24 ? 'urgent' : 'normal',
    timeLeft: timeLeft,
    hours: hours,
    minutes: minutes,
    message: `${hours}h ${minutes}m remaining`
  };
});

// Virtual for days until delivery
orderSchema.virtual('daysUntilDelivery').get(function() {
  if (!this.expectedDeliveryDate) return null;
  
  const now = new Date();
  const timeDiff = this.expectedDeliveryDate - now;
  return Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
});

module.exports = mongoose.model('Order', orderSchema);
