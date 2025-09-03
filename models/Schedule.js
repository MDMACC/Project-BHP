const mongoose = require('mongoose');

const scheduleSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  type: {
    type: String,
    enum: ['appointment', 'maintenance', 'repair', 'inspection', 'delivery', 'meeting', 'other'],
    required: true
  },
  customer: {
    name: String,
    phone: String,
    email: String,
    vehicle: {
      make: String,
      model: String,
      year: Number,
      licensePlate: String,
      vin: String
    }
  },
  startTime: {
    type: Date,
    required: true
  },
  endTime: {
    type: Date,
    required: true
  },
  duration: {
    type: Number, // in minutes
    required: true
  },
  status: {
    type: String,
    enum: ['scheduled', 'in_progress', 'completed', 'cancelled', 'no_show'],
    default: 'scheduled'
  },
  assignedTechnician: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  requiredParts: [{
    part: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Part'
    },
    quantity: {
      type: Number,
      default: 1
    },
    isAvailable: {
      type: Boolean,
      default: true
    }
  }],
  estimatedCost: {
    labor: {
      type: Number,
      default: 0
    },
    parts: {
      type: Number,
      default: 0
    },
    total: {
      type: Number,
      default: 0
    }
  },
  actualCost: {
    labor: {
      type: Number,
      default: 0
    },
    parts: {
      type: Number,
      default: 0
    },
    total: {
      type: Number,
      default: 0
    }
  },
  notes: String,
  reminders: [{
    type: {
      type: String,
      enum: ['email', 'sms', 'phone'],
      required: true
    },
    time: {
      type: Date,
      required: true
    },
    sent: {
      type: Boolean,
      default: false
    }
  }],
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  }
}, {
  timestamps: true
});

// Index for better query performance
scheduleSchema.index({ startTime: 1, endTime: 1 });
scheduleSchema.index({ status: 1 });
scheduleSchema.index({ assignedTechnician: 1 });

// Virtual for conflict detection
scheduleSchema.virtual('hasConflicts').get(function() {
  // This would be calculated by checking for overlapping schedules
  return false; // Placeholder
});

// Pre-save middleware to calculate total cost
scheduleSchema.pre('save', function(next) {
  if (this.estimatedCost.labor && this.estimatedCost.parts) {
    this.estimatedCost.total = this.estimatedCost.labor + this.estimatedCost.parts;
  }
  
  if (this.actualCost.labor && this.actualCost.parts) {
    this.actualCost.total = this.actualCost.labor + this.actualCost.parts;
  }
  
  next();
});

module.exports = mongoose.model('Schedule', scheduleSchema);
