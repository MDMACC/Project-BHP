const mongoose = require('mongoose');

const partSchema = new mongoose.Schema({
  partNumber: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    uppercase: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  category: {
    type: String,
    required: true,
    enum: ['engine', 'brake', 'transmission', 'electrical', 'body', 'interior', 'exhaust', 'suspension', 'other']
  },
  brand: {
    type: String,
    required: true,
    trim: true
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  cost: {
    type: Number,
    required: true,
    min: 0
  },
  quantityInStock: {
    type: Number,
    required: true,
    min: 0,
    default: 0
  },
  minimumStockLevel: {
    type: Number,
    default: 5
  },
  supplier: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Contact',
    required: true
  },
  location: {
    warehouse: String,
    shelf: String,
    bin: String
  },
  specifications: {
    weight: Number,
    dimensions: {
      length: Number,
      width: Number,
      height: Number
    },
    material: String,
    color: String
  },
  compatibleVehicles: [{
    make: String,
    model: String,
    year: {
      start: Number,
      end: Number
    }
  }],
  images: [String],
  isActive: {
    type: Boolean,
    default: true
  },
  lastRestocked: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Index for better search performance
partSchema.index({ partNumber: 1 });
partSchema.index({ name: 'text', description: 'text' });
partSchema.index({ category: 1, brand: 1 });

// Virtual for profit margin
partSchema.virtual('profitMargin').get(function() {
  if (this.cost > 0) {
    return ((this.price - this.cost) / this.cost * 100).toFixed(2);
  }
  return 0;
});

// Virtual for stock status
partSchema.virtual('stockStatus').get(function() {
  if (this.quantityInStock === 0) {
    return 'out_of_stock';
  } else if (this.quantityInStock <= this.minimumStockLevel) {
    return 'low_stock';
  }
  return 'in_stock';
});

module.exports = mongoose.model('Part', partSchema);
