📦 E-commerce Dataset Overview
Column	Description
User_ID	Unique identifier for each customer
Product_ID	Unique identifier for each product
Category	Product category (e.g., Sports, Toys)
Price (Rs.)	Original price
Discount (%)	Discount applied
Final_Price(Rs.)	Price after discount
Payment_Method	Payment method used
Purchase_Date	Date of purchase
🧠 Ontology Entities (to be auto-generated)
We'll infer the following for the demo ontology:

Product

Category

User

Purchase

PaymentMethod

And their relationships:

User → purchased → Product

Product → belongsTo → Category

Product → wasBoughtWith → PaymentMethod

