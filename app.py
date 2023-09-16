from flask import Flask
from flask import request
from flask import redirect
from flask import flash
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_alembic import Alembic
from flask import render_template

 
app = Flask(__name__)
app.config["SECRET_KEY"] = "123OK"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"

db = SQLAlchemy(app)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction = db.Column(db.Float, nullable=False)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    history_entry = db.Column(db.String(220), nullable=False)

# with app.app_context():
#     db.create_all()

alembic = Alembic()
alembic.init_app(app)

#http://127.0.0.1:5000/
@app.route("/")
def index():
    all_stocks = db.session.query(Stock).all()
    transactions = db.session.query(Account).first()
    return render_template("index.html", stocks=all_stocks, account = transactions)


#http://127.0.0.1:5000/balance
@app.route("/balance", methods=["GET", "POST"])
def balance():
    if request.method == "POST":
        account = db.session.query(Account).first()
        if not account:
            account = Account(transaction=0)
        transaction= float(request.form.get("Amount"))
        
        if account.transaction + transaction >0:
            account.transaction += transaction
            new_history_entry = History(history_entry=f"Balance update: {transaction} on the account.")
            db.session.add(account)
            db.session.add(new_history_entry)
            db.session.commit()
        
        return redirect(url_for("index"))
    return render_template("balance.html")

#http://127.0.0.1:5000/add-product
@app.route("/add-product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form.get("Product Name")
        size = request.form.get("Size")
        quantity = int(request.form.get("Quantity"))
        unit_price = float(request.form.get("Unit Price"))
        purchase = quantity*unit_price
        account = db.session.query(Account).first()


        if account.transaction >purchase:
            account.transaction -= purchase
            stock = db.session.query(Stock).filter(Stock.name == name).first()
            new_history_entry = History(history_entry=f"Purchasing {name} cost {purchase} euros. Brought {quantity} ")
            if stock:
                stock.quantity += quantity
            else:
                stock = Stock(name = name,
                size = size,
                quantity = quantity,
                unit_price = unit_price,
                )
        
            db.session.add(stock)
            db.session.add(account)
            db.session.add(new_history_entry)
            db.session.commit()
        
        else:
            flash("No enough balance to purchase these products!")
            
        return redirect(url_for("index"))
    return render_template("add_product.html")


@app.route("/add-dedu/<typ>/<stock_id>/")
def update_products(typ, stock_id):
    stock_id = int(stock_id)
    stock = db.session.query(Stock).filter(Stock.id == stock.id).first()

    if typ == "add":
        stock.quantity += 1

    elif typ == "dedu":
        stock.quantity -= 1

    db.session.add(stock)
    db.session.commit()
    return redirect(url_for("index"))
        



#http://127.0.0.1:5000/sell-product
@app.route("/sell-product", methods=["GET", "POST"])
def sell_product():
    if request.method == "POST":
        name = request.form.get("Product Name")
        quantity = int(request.form.get("Quantity"))
        unit_price = float(request.form.get("Unit Price"))
        sale = quantity*unit_price
        account = db.session.query(Account).first()
        stock = db.session.query(Stock).filter(Stock.name == name).first()
        
        if stock:
            stock.quantity -= quantity
            account.transaction += sale
            new_history_entry = History(history_entry=f"Selling {name} for {quantity} units brought {sale} euros revenue.")
            db.session.add(account)
            db.session.add(new_history_entry)
            db.session.commit()
        else:
           flash("This product is not in the stock. Please enter a valid product type.")
        
        return redirect(url_for("index"))
    return render_template("sell_product.html")

# #http://127.0.0.1:5000/history
@app.route("/history", methods=["GET", "POST"])
def history():
    history = db.session.query(History)
    # if request.method == "POST":
    #     history = db.session.query(History).all()
    return render_template("history.html", history = history)

#http://127.0.0.1:5000/history/2/5
# @app.route("/history/<int:start>/<int:end>/", methods=["GET", "POST"])
# def history(start, end):
#     if request.method == "POST":
#         history = db.session.query(History).all()
#         history= history[start:end]
#         return render_template("history.html", history = history)


if __name__ == '__main__':
    app.run(debug=True, port=8088)
