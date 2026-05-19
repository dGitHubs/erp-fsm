# ERP FSM - Project Status

## Project Overview

ERP FSM is a manufacturing-oriented ERP API focused on the operational flow from product definition to material planning and production readiness.

The current scope covers:
- customer management
- product management
- material management
- bill of materials (BOM)
- manufacturing orders
- material cost calculation
- material requirements planning
- material availability checks

---

## Current Milestone

The project now supports the full planning flow for a manufacturing order:

1. define products and materials
2. link materials to products through a BOM
3. create manufacturing orders
4. calculate required materials
5. check whether current stock is sufficient to produce

This provides a strong base for moving into stock consumption and manufacturing execution.

---

## Completed

### Core API Foundation
- [x] Health check endpoint
- [x] FastAPI application structure
- [x] SQLAlchemy models and database integration
- [x] Pydantic schemas
- [x] Automated test setup

### Customers
- [x] Create customer
- [x] List customers
- [x] Get customer by id
- [x] Validation and automated tests

### Products
- [x] Create product
- [x] List products
- [x] Get product by id
- [x] Validation for units and dimensions
- [x] Automated tests

### Materials
- [x] Create material
- [x] List materials
- [x] Get material by id
- [x] Validation for units and unit cost
- [x] Support `quantity_on_hand`
- [x] Automated tests

### Bill of Materials (Product Materials)
- [x] Link materials to products
- [x] Define required quantity per material
- [x] List product-material links
- [x] Get product-material link by id
- [x] Automated tests

### Manufacturing Orders
- [x] Create manufacturing order
- [x] List manufacturing orders
- [x] Get manufacturing order by id
- [x] Validation for order status and quantity
- [x] Automated tests

### Costing
- [x] Compute product material cost
- [x] Support products with no BOM lines
- [x] Automated tests

### Manufacturing Planning
- [x] Compute material requirements for a manufacturing order
- [x] Compute material availability for a manufacturing order
- [x] Detect whether an order can be produced with current stock
- [x] Automated tests

---

## Next Milestone

### Material Consumption
The next logical step is to move from planning to execution.

Planned work:
- [ ] Add endpoint to consume materials for a manufacturing order
- [ ] Decrease `quantity_on_hand` based on BOM × manufacturing order quantity
- [ ] Prevent consumption when stock is insufficient
- [ ] Return a material consumption summary
- [ ] Add automated tests

This will make the system capable of not only checking production readiness, but also reflecting stock usage when production starts or completes.

---

## Future Backlog

### Inventory Management
- [ ] Stock movement history
- [ ] Material receiving / replenishment
- [ ] Inventory adjustments
- [ ] Material reservation for manufacturing orders

### Manufacturing Execution
- [ ] Richer manufacturing order lifecycle
- [ ] Work operations / routing steps
- [ ] Labor and time tracking
- [ ] Production completion workflow

### Supply and Business Features
- [ ] Purchasing support
- [ ] Sales quotes
- [ ] Pricing rules
- [ ] Margin tracking

---

## Quality Status

Current validated status:
- [x] Linting passing
- [x] Test suite passing
- [x] Manufacturing planning flow implemented
- [x] Material availability flow implemented

> Latest verified status: 54 tests passing