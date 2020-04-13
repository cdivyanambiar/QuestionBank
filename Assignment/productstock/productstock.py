#dietfact Application
from openerp import models, fields, api

#Extend product.template with calories
class product_stock(models.Model):
    _name = 'product.my_product_stock'
     
    product_id = fields.Many2one('product.template','Product')
    createdon = fields.Date("created On") 
    qty_ordered = fields.Float("Quantity Ordered")
    qty_delivered = fields.Float("Quantity Delievered")
    remainingstock = fields.Integer("Remaining Stock of Item")
    

class product_product_template(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    order_ids = fields.One2many('product.my_product_stock', 'product_id')
    
    @api.one
    @api.depends('order_ids')
    def _calcremaining(self):
        current_stock = 0
        quantity_ordered = 0
        quantity_delievered = 0;
        for productref in self.order_ids:
            if productref.product_id.name == self.name:
                quantity_ordered = quantity_ordered + productref.qty_ordered
                quantity_delievered = quantity_delievered + productref.qty_delivered
                current_stock = quantity_ordered - quantity_delievered
        self.remainingstock = current_stock
    remainingstock = fields.Float(String="Quantity Remainings", Store=True, compute="_calcremaining")