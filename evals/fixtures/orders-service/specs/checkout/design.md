# Checkout — design

`OrderService.submit()` looks up the order id before charging; a repeated order id
returns the first charge instead of charging again.

Status: Draft
