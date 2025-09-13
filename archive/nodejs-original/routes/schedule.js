const express = require('express');
const { body, validationResult, query } = require('express-validator');
const Schedule = require('../models/Schedule');
const Part = require('../models/Part');
const { auth, adminAuth } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/schedule
// @desc    Get all scheduled appointments with filtering
// @access  Private
router.get('/', auth, [
  query('startDate').optional().isISO8601().withMessage('Start date must be a valid date'),
  query('endDate').optional().isISO8601().withMessage('End date must be a valid date'),
  query('status').optional().isIn(['scheduled', 'in_progress', 'completed', 'cancelled', 'no_show']),
  query('type').optional().isIn(['appointment', 'maintenance', 'repair', 'inspection', 'delivery', 'meeting', 'other']),
  query('technician').optional().isMongoId()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Build filter object
    const filter = {};
    
    if (req.query.startDate && req.query.endDate) {
      filter.startTime = {
        $gte: new Date(req.query.startDate),
        $lte: new Date(req.query.endDate)
      };
    } else if (req.query.startDate) {
      filter.startTime = { $gte: new Date(req.query.startDate) };
    } else if (req.query.endDate) {
      filter.startTime = { $lte: new Date(req.query.endDate) };
    }
    
    if (req.query.status) {
      filter.status = req.query.status;
    }
    
    if (req.query.type) {
      filter.type = req.query.type;
    }
    
    if (req.query.technician) {
      filter.assignedTechnician = req.query.technician;
    }

    const schedules = await Schedule.find(filter)
      .populate('assignedTechnician', 'username')
      .populate('requiredParts.part', 'partNumber name brand price')
      .populate('createdBy', 'username')
      .sort({ startTime: 1 });

    res.json(schedules);
  } catch (error) {
    console.error('Get schedules error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/schedule/:id
// @desc    Get single schedule
// @access  Private
router.get('/:id', auth, async (req, res) => {
  try {
    const schedule = await Schedule.findById(req.params.id)
      .populate('assignedTechnician', 'username email')
      .populate('requiredParts.part', 'partNumber name brand price quantityInStock')
      .populate('createdBy', 'username email');

    if (!schedule) {
      return res.status(404).json({ message: 'Schedule not found' });
    }

    res.json(schedule);
  } catch (error) {
    console.error('Get schedule error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/schedule
// @desc    Create new schedule
// @access  Private (Admin/Manager)
router.post('/', adminAuth, [
  body('title').notEmpty().withMessage('Title is required'),
  body('type').isIn(['appointment', 'maintenance', 'repair', 'inspection', 'delivery', 'meeting', 'other']).withMessage('Invalid schedule type'),
  body('startTime').isISO8601().withMessage('Start time must be a valid date'),
  body('endTime').isISO8601().withMessage('End time must be a valid date'),
  body('duration').isInt({ min: 15 }).withMessage('Duration must be at least 15 minutes'),
  body('customer.name').optional().isString(),
  body('customer.phone').optional().isString(),
  body('customer.email').optional().isEmail().withMessage('Customer email must be valid'),
  body('assignedTechnician').optional().isMongoId().withMessage('Invalid technician ID')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Check for scheduling conflicts
    const startTime = new Date(req.body.startTime);
    const endTime = new Date(req.body.endTime);

    if (req.body.assignedTechnician) {
      const conflict = await Schedule.findOne({
        assignedTechnician: req.body.assignedTechnician,
        status: { $in: ['scheduled', 'in_progress'] },
        $or: [
          {
            startTime: { $lt: endTime },
            endTime: { $gt: startTime }
          }
        ]
      });

      if (conflict) {
        return res.status(400).json({ 
          message: 'Technician has a scheduling conflict during this time' 
        });
      }
    }

    // Check if required parts are available
    if (req.body.requiredParts && req.body.requiredParts.length > 0) {
      for (const requiredPart of req.body.requiredParts) {
        const part = await Part.findById(requiredPart.part);
        if (!part) {
          return res.status(400).json({ 
            message: `Part with ID ${requiredPart.part} not found` 
          });
        }
        
        if (part.quantityInStock < requiredPart.quantity) {
          requiredPart.isAvailable = false;
        }
      }
    }

    const schedule = new Schedule({
      ...req.body,
      createdBy: req.user._id
    });

    await schedule.save();
    await schedule.populate('assignedTechnician', 'username');
    await schedule.populate('requiredParts.part', 'partNumber name brand price');

    res.status(201).json(schedule);
  } catch (error) {
    console.error('Create schedule error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   PUT /api/schedule/:id
// @desc    Update schedule
// @access  Private (Admin/Manager)
router.put('/:id', adminAuth, [
  body('title').optional().notEmpty().withMessage('Title cannot be empty'),
  body('type').optional().isIn(['appointment', 'maintenance', 'repair', 'inspection', 'delivery', 'meeting', 'other']).withMessage('Invalid schedule type'),
  body('startTime').optional().isISO8601().withMessage('Start time must be a valid date'),
  body('endTime').optional().isISO8601().withMessage('End time must be a valid date'),
  body('status').optional().isIn(['scheduled', 'in_progress', 'completed', 'cancelled', 'no_show']).withMessage('Invalid status')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const schedule = await Schedule.findById(req.params.id);
    if (!schedule) {
      return res.status(404).json({ message: 'Schedule not found' });
    }

    // Check for scheduling conflicts if time or technician is being changed
    if ((req.body.startTime || req.body.endTime || req.body.assignedTechnician) && 
        schedule.status === 'scheduled') {
      
      const startTime = new Date(req.body.startTime || schedule.startTime);
      const endTime = new Date(req.body.endTime || schedule.endTime);
      const technician = req.body.assignedTechnician || schedule.assignedTechnician;

      if (technician) {
        const conflict = await Schedule.findOne({
          _id: { $ne: schedule._id },
          assignedTechnician: technician,
          status: { $in: ['scheduled', 'in_progress'] },
          $or: [
            {
              startTime: { $lt: endTime },
              endTime: { $gt: startTime }
            }
          ]
        });

        if (conflict) {
          return res.status(400).json({ 
            message: 'Technician has a scheduling conflict during this time' 
          });
        }
      }
    }

    Object.assign(schedule, req.body);
    await schedule.save();

    await schedule.populate('assignedTechnician', 'username');
    await schedule.populate('requiredParts.part', 'partNumber name brand price');

    res.json(schedule);
  } catch (error) {
    console.error('Update schedule error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   DELETE /api/schedule/:id
// @desc    Cancel schedule
// @access  Private (Admin/Manager)
router.delete('/:id', adminAuth, async (req, res) => {
  try {
    const schedule = await Schedule.findById(req.params.id);
    if (!schedule) {
      return res.status(404).json({ message: 'Schedule not found' });
    }

    if (schedule.status === 'completed') {
      return res.status(400).json({ message: 'Cannot cancel completed schedule' });
    }

    schedule.status = 'cancelled';
    await schedule.save();

    res.json({ message: 'Schedule cancelled successfully' });
  } catch (error) {
    console.error('Cancel schedule error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/schedule/calendar/:date
// @desc    Get schedule for a specific date
// @access  Private
router.get('/calendar/:date', auth, async (req, res) => {
  try {
    const date = new Date(req.params.date);
    const startOfDay = new Date(date.setHours(0, 0, 0, 0));
    const endOfDay = new Date(date.setHours(23, 59, 59, 999));

    const schedules = await Schedule.find({
      startTime: { $gte: startOfDay, $lte: endOfDay },
      status: { $ne: 'cancelled' }
    })
    .populate('assignedTechnician', 'username')
    .populate('requiredParts.part', 'partNumber name')
    .sort({ startTime: 1 });

    res.json(schedules);
  } catch (error) {
    console.error('Get calendar schedule error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/schedule/technician/:technicianId
// @desc    Get schedules for a specific technician
// @access  Private
router.get('/technician/:technicianId', auth, [
  query('startDate').optional().isISO8601(),
  query('endDate').optional().isISO8601()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const filter = { assignedTechnician: req.params.technicianId };
    
    if (req.query.startDate && req.query.endDate) {
      filter.startTime = {
        $gte: new Date(req.query.startDate),
        $lte: new Date(req.query.endDate)
      };
    }

    const schedules = await Schedule.find(filter)
      .populate('assignedTechnician', 'username')
      .populate('requiredParts.part', 'partNumber name')
      .sort({ startTime: 1 });

    res.json(schedules);
  } catch (error) {
    console.error('Get technician schedule error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/schedule/:id/start
// @desc    Start a scheduled appointment
// @access  Private
router.post('/:id/start', auth, async (req, res) => {
  try {
    const schedule = await Schedule.findById(req.params.id);
    if (!schedule) {
      return res.status(404).json({ message: 'Schedule not found' });
    }

    if (schedule.status !== 'scheduled') {
      return res.status(400).json({ message: 'Can only start scheduled appointments' });
    }

    schedule.status = 'in_progress';
    await schedule.save();

    res.json(schedule);
  } catch (error) {
    console.error('Start schedule error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/schedule/:id/complete
// @desc    Complete a scheduled appointment
// @access  Private
router.post('/:id/complete', auth, [
  body('actualCost.labor').optional().isFloat({ min: 0 }),
  body('actualCost.parts').optional().isFloat({ min: 0 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const schedule = await Schedule.findById(req.params.id);
    if (!schedule) {
      return res.status(404).json({ message: 'Schedule not found' });
    }

    if (schedule.status !== 'in_progress') {
      return res.status(400).json({ message: 'Can only complete in-progress appointments' });
    }

    schedule.status = 'completed';
    
    if (req.body.actualCost) {
      schedule.actualCost = { ...schedule.actualCost, ...req.body.actualCost };
    }

    // Update inventory if parts were used
    if (schedule.requiredParts && schedule.requiredParts.length > 0) {
      for (const requiredPart of schedule.requiredParts) {
        const part = await Part.findById(requiredPart.part);
        if (part && requiredPart.quantity) {
          part.quantityInStock = Math.max(0, part.quantityInStock - requiredPart.quantity);
          await part.save();
        }
      }
    }

    await schedule.save();
    await schedule.populate('assignedTechnician', 'username');
    await schedule.populate('requiredParts.part', 'partNumber name brand');

    res.json(schedule);
  } catch (error) {
    console.error('Complete schedule error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
