# ERP FSM - Project Status

## Done

### Core API
- Health check endpoint
- FastAPI app structure
- SQLAlchemy models and database integration
- Pydantic schemas
- CRUD foundations for core resources

### Customers
- Create customer
- List customers
- Get customer by id
- Validation and automated tests

### Products
- Create product
- List products
- Get product by id
- Validation for unit and dimensions
- Automated tests

### Materials
- Create material
- List materials
- Get material by id
- Validation for unit and unit cost
- Support for `quantity_on_hand`
- Automated tests

### Product Materials / BOM
- Link materials to products
- Define quantity of material required per product
- List product materials
- Get product material by id
- Automated tests

### Manufacturing Orders
- Create manufacturing order
- List manufacturing orders
- Get manufacturing order by id
- Validation for status and quantity
- Automated tests

### Costing
- Get product material cost
- Support products with no materials
- Automated tests

### Manufacturing Planning
- Get manufacturing order material requirements
- Get manufacturing order material availability
- Detect whether an order can be produced with current stock
- Automated tests

## Next
- Consume materials for a manufacturing order
- Decrease `quantity_on_hand` based on BOM × order quantity
- Prevent consumption when stock is insufficient
- Return a consumption summary response

## Later
- Stock movement history
- Material receiving / replenishment
- Inventory adjustments
- Material reservation for manufacturing orders
- Richer manufacturing order lifecycle
- Work operations / routing steps
- Labor / time tracking
- Purchasing support
- Sales quotes / pricing / margin