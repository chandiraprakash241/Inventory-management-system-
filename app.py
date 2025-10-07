from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Product {self.product_id}: {self.name}>'

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Location {self.location_id}: {self.name}>'

class ProductMovement(db.Model):
    movement_id = db.Column(db.String(50), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='movements')
    from_loc = db.relationship('Location', foreign_keys=[from_location], backref='movements_from')
    to_loc = db.relationship('Location', foreign_keys=[to_location], backref='movements_to')
    
    def __repr__(self):
        return f'<Movement {self.movement_id}: {self.qty} of {self.product_id} from {self.from_location} to {self.to_location}>'

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Product Routes
@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_id = request.form['product_id']
        name = request.form['name']
        description = request.form['description']
        
        if Product.query.filter_by(product_id=product_id).first():
            flash('Product ID already exists!', 'error')
            return render_template('add_product.html')
        
        product = Product(product_id=product_id, name=name, description=description)
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('add_product.html')

@app.route('/products/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products'))

# Location Routes
@app.route('/locations')
def locations():
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location_id = request.form['location_id']
        name = request.form['name']
        address = request.form['address']
        
        if Location.query.filter_by(location_id=location_id).first():
            flash('Location ID already exists!', 'error')
            return render_template('add_location.html')
        
        location = Location(location_id=location_id, name=name, address=address)
        db.session.add(location)
        db.session.commit()
        flash('Location added successfully!', 'success')
        return redirect(url_for('locations'))
    
    return render_template('add_location.html')

@app.route('/locations/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    
    if request.method == 'POST':
        location.name = request.form['name']
        location.address = request.form['address']
        db.session.commit()
        flash('Location updated successfully!', 'success')
        return redirect(url_for('locations'))
    
    return render_template('edit_location.html', location=location)

@app.route('/locations/delete/<location_id>')
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    flash('Location deleted successfully!', 'success')
    return redirect(url_for('locations'))

# Product Movement Routes
@app.route('/movements')
def movements():
    movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movements.html', movements=movements)

@app.route('/movements/add', methods=['GET', 'POST'])
def add_movement():
    if request.method == 'POST':
        movement_id = request.form['movement_id']
        from_location = request.form['from_location'] if request.form['from_location'] else None
        to_location = request.form['to_location'] if request.form['to_location'] else None
        product_id = request.form['product_id']
        qty = int(request.form['qty'])
        
        if ProductMovement.query.filter_by(movement_id=movement_id).first():
            flash('Movement ID already exists!', 'error')
            return render_template('add_movement.html', 
                                 products=Product.query.all(), 
                                 locations=Location.query.all())
        
        if not from_location and not to_location:
            flash('Either from_location or to_location must be specified!', 'error')
            return render_template('add_movement.html', 
                                 products=Product.query.all(), 
                                 locations=Location.query.all())
        
        movement = ProductMovement(
            movement_id=movement_id,
            from_location=from_location,
            to_location=to_location,
            product_id=product_id,
            qty=qty
        )
        db.session.add(movement)
        db.session.commit()
        flash('Movement added successfully!', 'success')
        return redirect(url_for('movements'))
    
    return render_template('add_movement.html', 
                         products=Product.query.all(), 
                         locations=Location.query.all())

@app.route('/movements/edit/<movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    
    if request.method == 'POST':
        movement.from_location = request.form['from_location'] if request.form['from_location'] else None
        movement.to_location = request.form['to_location'] if request.form['to_location'] else None
        movement.product_id = request.form['product_id']
        movement.qty = int(request.form['qty'])
        
        if not movement.from_location and not movement.to_location:
            flash('Either from_location or to_location must be specified!', 'error')
            return render_template('edit_movement.html', 
                                 movement=movement,
                                 products=Product.query.all(), 
                                 locations=Location.query.all())
        
        db.session.commit()
        flash('Movement updated successfully!', 'success')
        return redirect(url_for('movements'))
    
    return render_template('edit_movement.html', 
                         movement=movement,
                         products=Product.query.all(), 
                         locations=Location.query.all())

@app.route('/movements/delete/<movement_id>')
def delete_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    db.session.delete(movement)
    db.session.commit()
    flash('Movement deleted successfully!', 'success')
    return redirect(url_for('movements'))

# Balance Report
@app.route('/balance')
def balance():
    # Get all products and locations
    products = Product.query.all()
    locations = Location.query.all()
    
    # Calculate balance for each product in each location
    balance_data = []
    
    for product in products:
        for location in locations:
            # Calculate incoming quantity (to_location = this location)
            incoming = db.session.query(db.func.sum(ProductMovement.qty)).filter(
                ProductMovement.to_location == location.location_id,
                ProductMovement.product_id == product.product_id
            ).scalar() or 0
            
            # Calculate outgoing quantity (from_location = this location)
            outgoing = db.session.query(db.func.sum(ProductMovement.qty)).filter(
                ProductMovement.from_location == location.location_id,
                ProductMovement.product_id == product.product_id
            ).scalar() or 0
            
            balance = incoming - outgoing
            
            if balance > 0:  # Only show locations with positive balance
                balance_data.append({
                    'product': product.name,
                    'location': location.name,
                    'qty': balance
                })
    
    return render_template('balance.html', balance_data=balance_data)

# Simple seed route to add sample data
@app.route('/seed')
def seed():
    # Create products
    sample_products = [
        ('P-A', 'Product A', 'Sample A'),
        ('P-B', 'Product B', 'Sample B'),
        ('P-C', 'Product C', 'Sample C'),
        ('P-D', 'Product D', 'Sample D'),
    ]
    for pid, name, desc in sample_products:
        if not Product.query.get(pid):
            db.session.add(Product(product_id=pid, name=name, description=desc))

    # Create locations
    sample_locations = [
        ('L-X', 'Location X', 'Block X'),
        ('L-Y', 'Location Y', 'Block Y'),
        ('L-Z', 'Location Z', 'Block Z'),
    ]
    for lid, name, addr in sample_locations:
        if not Location.query.get(lid):
            db.session.add(Location(location_id=lid, name=name, address=addr))

    db.session.commit()

    # Create sample movements
    movements = [
        ('M-001', None, 'L-X', 'P-A', 10),  # incoming to X
        ('M-002', None, 'L-X', 'P-B', 5),   # incoming to X
        ('M-003', 'L-X', 'L-Y', 'P-A', 3),  # move A X->Y
        ('M-004', None, 'L-Y', 'P-C', 8),   # incoming to Y
        ('M-005', 'L-Y', None, 'P-C', 2),   # outgoing from Y
        ('M-006', 'L-X', 'L-Z', 'P-B', 2),  # move B X->Z
        ('M-007', None, 'L-Z', 'P-D', 12),  # incoming to Z
        ('M-008', 'L-Z', 'L-X', 'P-D', 4),  # move D Z->X
    ]

    for mid, f, t, pid, q in movements:
        if not ProductMovement.query.get(mid):
            db.session.add(ProductMovement(
                movement_id=mid,
                from_location=f,
                to_location=t,
                product_id=pid,
                qty=q
            ))

    db.session.commit()
    flash('Sample data seeded.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
