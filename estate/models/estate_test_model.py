from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class TestModel(models.Model):
    _name = "estate.property"
    _description = "My first Test Model for my first test module"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(compute="_compute_description")
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=(datetime.now()+relativedelta(month=+3)))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden area (sqm)")
    
    garden_orientation = fields.Selection(string="Garden Orientation",
                                          selection=[("north", "North"),
                                                     ("south", "South"),
                                                     ("west", "West"),
                                                     ("east", "East")])
    state = fields.Selection(selection=[("new", "New"),
                                       ("offer_received", "Offer Received"),
                                       ("offer_accepted", "Offer Accepted"),
                                       ("sold", "Sold"),
                                       ("canceled", "Canceled")],
                            copy=False, required=True, default="new")

    property_type_id = fields.Many2one('estate.property.type', string="Property Type")
    salesperson = fields.Many2one('res.users', string="Odoo user who sold it",
                                    default=lambda self: self.env.user, index=True)
    buyer = fields.Many2one('res.partner', string="Buyer", copy=False, readonly=True)
    tag_ids = fields.Many2many('estate.property.tag', string="Tag")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")

    total_area = fields.Float(compute="_compute_total_area", string="Total area (sqm)")

    best_offer = fields.Float(compute="_compute_best_offer", string="Best offer")

    _sql_constraints = [
      ('check_expected_price', 'CHECK(expected_price > 0)', 
        'The expected price should be positive'),
      ('check_selling_price', 'CHECK(selling_price > 0)', 
        'The selling price should be positive')
    ]

    _order = "id desc"

    @api.ondelete(at_uninstall=False)
    def _check_ondelete_state(self):
      for record in self:
        print("aa")
        print(record.state)
        print("aa")
        if record.state not in ['new', 'canceled']:  
          raise UserError('You can not delete if state is not New or Canceled')

    @api.constrains('selling_price')
    def _check_selling_price(self):
      for record in self:
        if (record.selling_price / record.expected_price) * 100 < 90:
          raise ValidationError('The selling price must be greater than 90% of expected price')

    @api.onchange('garden')
    def _onchange_garden_checkbox(self):
      if self.garden:
        self.garden_area = 10
        self.garden_orientation = "north"
      else:
        self.garden_area = 0
        self.garden_orientation = ""

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
      for record in self:
        price_list = record.offer_ids.mapped('price')
        record.best_offer = price_list[0] if len(price_list) > 0 else 0 

    @api.depends('garden_area', 'living_area')
    def _compute_total_area(self):
      for record in self:
        record.total_area = record.living_area + record.garden_area

    @api.depends('salesperson')
    def _compute_description(self):
      for record in self:
        record.description = f"This is the salesperson: {record.salesperson.name}"

    def property_status_sold(self):
      for record in self:
        if record.state == "canceled":
          raise UserError('Canceled property can not be sold')
        record.state = "sold"
        return True

    def property_status_cancel(self):
      for record in self:
        if record.state == "sold":
          raise UserError('Sold property can not be canceled')
        record.state = "canceled"
        return True


class TestModelType(models.Model):
  _name = "estate.property.type"

  name = fields.Char(required=True)
  property_ids = fields.One2many('estate.property', 'property_type_id')
  sequance = fields.Integer('Sequance', default="1", 
                            help="Used to order types. Lower is better")
  offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
  offer_count = fields.Integer(compute="calculate_offers")

  _sql_constraints = [
      ('check_name', 'UNIQUE(name)', 
        'The name should be unique')
    ]

  _order = "name"

  # @api.depends('offer_ids')
  def calculate_offers(self):
    for record in self:
      record.offer_count = len(record.offer_ids.mapped('status'))

class TestModelTag(models.Model):
  _name = "estate.property.tag"

  name = fields.Char(required=True)
  color = fields.Integer()

  _sql_constraints = [
      ('check_name', 'UNIQUE(name)', 
        'The name should be unique')
    ]

  _order = "name"


class TestModelOffer(models.Model):
  _name = "estate.property.offer"

  price = fields.Float()
  status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
                            copy=False)
  partner_id = fields.Many2one('res.partner', required=True, default=lambda self: self.env.user)
  property_id = fields.Many2one('estate.property', required=True)
  validity = fields.Integer(default=7, string="Valid days")
  date_deadline = fields.Date(string="Deadline date", 
                              compute="_compute_date_deadline",
                              inverse="_inverse_date_deadline")
  property_type_id = fields.Many2one(related="property_id.property_type_id")

  _sql_constraints = [
      ('check_price', 'CHECK(price > 0)', 
        'The price should be positive')
    ]

  _order = "price desc"

  @api.model
  def create(self, vals):
    property_obj = self.env['estate.property'].browse(vals['property_id'])
    list_of_prices = property_obj.mapped('offer_ids.price')
    if len(list_of_prices) != 0:
      if vals['price'] < list_of_prices[0]:
        raise UserError(f"Price must be higher then {list_of_prices[0]}")
    property_obj.state = 'offer_received'
    return super(TestModelOffer, self).create(vals)

  @api.depends('validity')
  def _compute_date_deadline(self):
    for record in self:
      created_date = datetime.now()
      try:
        created_date = record.created_date
      except AttributeError:
        pass 
      record.date_deadline = created_date + relativedelta(days=record.validity)

  def _inverse_date_deadline(self):
    for record in self:
      created_date = datetime.strptime(
            str(record.create_date.now().date()), 
            "%Y-%m-%d")
      deadline_date = datetime.strptime(
            str(record.date_deadline),
            "%Y-%m-%d")
      date_days = deadline_date - created_date
      record.validity =  date_days.days

  def confirm_property_offer(self):
    for record in self:
      if (record.status != "accepted") and \
      ('accepted'  not in self.property_id.offer_ids.mapped('status')):
        record.status = "accepted"
        record.property_id.selling_price = record.price
        record.property_id.buyer = record.partner_id
      else:
        raise UserError('Accepted offer already exsists')
    return True

  def cancel_property_offer(self):
    for record in self:
      if record.status != "refused":
        if record.status == "accepted":
          record.property_id.selling_price = 0
          record.property_id.buyer = None
        record.status = "refused"
    return True

