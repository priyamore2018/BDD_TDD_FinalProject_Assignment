# features/products.feature
# Task 6: BDD Scenarios for the Product Catalogue REST API
#
# Covers: Read / Update / Delete / List all /
#         Search by Name / Search by Category / Search by Availability

Feature: Product Catalogue REST API
    As an eCommerce platform owner
    I need a REST API to manage my product catalogue
    So that I can create, read, update, delete, and query products

    Background: A known set of products exists in the system
        Given the following products exist
          | name         | description                  | price  | available | category   |
          | Hammer       | 16oz steel claw hammer       | 14.99  | True      | TOOLS      |
          | Screwdriver  | Flat-head screwdriver        | 6.99   | True      | TOOLS      |
          | Bread        | Whole wheat sliced bread     | 2.49   | True      | FOOD       |
          | Milk         | Semi-skimmed 2 litre         | 1.29   | False     | FOOD       |
          | T-Shirt      | Cotton crew-neck t-shirt     | 12.99  | True      | CLOTHS     |
          | Drill        | Cordless 18V drill           | 79.99  | False     | TOOLS      |
          | Frying Pan   | Non-stick 28cm frying pan    | 24.99  | True      | HOUSEWARES |
          | Engine Oil   | 5W-30 fully synthetic 5L     | 34.99  | True      | AUTOMOTIVE |


    ##################################################################
    # READ
    ##################################################################

    Scenario: Read an existing product by id
        When I list all products
        Then I save the product id
        When I retrieve the product with id "1"
        Then the response should be OK
        And  the response JSON field "name" should be "Hammer"
        And  the response JSON field "category" should be "TOOLS"
        And  the response JSON field "price" should be "14.99"

    Scenario: Read a product that does not exist
        When I retrieve the product with id "99999"
        Then the response should be Not Found

    Scenario: Read a product returns all expected fields
        When I retrieve the product with id "1"
        Then the response should be OK
        And  the response body should contain "id"
        And  the response body should contain "name"
        And  the response body should contain "description"
        And  the response body should contain "price"
        And  the response body should contain "available"
        And  the response body should contain "category"


    ##################################################################
    # UPDATE
    ##################################################################

    Scenario: Update an existing product
        When I update the product with id "1" with
          | name         | description               | price  | available | category |
          | Claw Hammer  | Heavy-duty 20oz hammer    | 24.99  | True      | TOOLS    |
        Then the response should be OK
        And  the response JSON field "name" should be "Claw Hammer"
        And  the response JSON field "price" should be "24.99"

    Scenario: Update a product and verify changes are persisted
        When I update the product with id "1" with
          | name     | description       | price | available | category |
          | Big Drill | Industrial drill | 149.99 | True     | TOOLS    |
        Then the response should be OK
        When I retrieve the product with id "1"
        Then the response JSON field "name" should be "Big Drill"
        And  the response JSON field "price" should be "149.99"

    Scenario: Update a product that does not exist
        When I send a PUT request to "/products/99999" with body
          """
          {
              "name": "Ghost Product",
              "description": "This product does not exist",
              "price": "1.00",
              "available": true,
              "category": "UNKNOWN"
          }
          """
        Then the response should be Not Found

    Scenario: Update a product to be unavailable
        When I update the product with id "1" with
          | name   | description        | price | available | category |
          | Hammer | Discontinued model | 14.99 | False     | TOOLS    |
        Then the response should be OK
        And  the response JSON field "available" should be false


    ##################################################################
    # DELETE
    ##################################################################

    Scenario: Delete an existing product
        When I delete the product with id "1"
        Then the response should be No Content
        When I retrieve the product with id "1"
        Then the response should be Not Found

    Scenario: Delete a product that does not exist returns 204 (idempotent)
        When I delete the product with id "99999"
        Then the response should be No Content

    Scenario: Deleting one product does not affect others
        When I delete the product with id "1"
        Then the response should be No Content
        When I list all products
        Then the response should be OK
        # 7 products remain (8 seeded - 1 deleted)
        And  the response list should have "7" item(s)


    ##################################################################
    # LIST ALL
    ##################################################################

    Scenario: List all products returns every seeded product
        When I list all products
        Then the response should be OK
        And  the response list should have "8" item(s)

    Scenario: List all products on an empty database
        Given there are no products in the database
        # Background has already run, but the env wipes the DB on next scenario.
        # This scenario uses a fresh database seeded with nothing extra.
        When I list all products
        Then the response should be OK

    Scenario: List all products returns a JSON array
        When I list all products
        Then the response should be OK
        And  the response list should have "8" item(s)


    ##################################################################
    # SEARCH BY NAME
    ##################################################################

    Scenario: Search by name returns matching products
        When I search for products by name "Hammer"
        Then the response should be OK
        And  the response list should have "1" item(s)
        And  every item in the list should have name "Hammer"

    Scenario: Search by name with multiple matches
        When I search for products by name "Bread"
        Then the response should be OK
        And  every item in the list should have name "Bread"

    Scenario: Search by name with no matches returns empty list
        When I search for products by name "Unicycle"
        Then the response should be OK
        And  the response list should be empty

    Scenario: Search by name is case-sensitive
        When I search for products by name "hammer"
        Then the response should be OK
        And  the response list should be empty


    ##################################################################
    # SEARCH BY CATEGORY
    ##################################################################

    Scenario: Search by category TOOLS
        When I search for products by category "TOOLS"
        Then the response should be OK
        And  the response list should have "3" item(s)
        And  every item in the list should have category "TOOLS"

    Scenario: Search by category FOOD
        When I search for products by category "FOOD"
        Then the response should be OK
        And  the response list should have "2" item(s)
        And  every item in the list should have category "FOOD"

    Scenario: Search by category CLOTHS
        When I search for products by category "CLOTHS"
        Then the response should be OK
        And  the response list should have "1" item(s)
        And  every item in the list should have category "CLOTHS"

    Scenario: Search by category HOUSEWARES
        When I search for products by category "HOUSEWARES"
        Then the response should be OK
        And  the response list should have "1" item(s)
        And  every item in the list should have category "HOUSEWARES"

    Scenario: Search by category AUTOMOTIVE
        When I search for products by category "AUTOMOTIVE"
        Then the response should be OK
        And  the response list should have "1" item(s)
        And  every item in the list should have category "AUTOMOTIVE"

    Scenario: Search by an invalid category returns 400
        When I search for products by category "INVALID_CATEGORY"
        Then the response status code should be "400"

    Scenario: Search by category with no matching products returns empty list
        When I search for products by category "UNKNOWN"
        Then the response should be OK
        And  the response list should be empty


    ##################################################################
    # SEARCH BY AVAILABILITY
    ##################################################################

    Scenario: Search for available products
        When I search for products by availability "true"
        Then the response should be OK
        And  the response list should have "6" item(s)
        And  every item in the list should have available "True"

    Scenario: Search for unavailable products
        When I search for products by availability "false"
        Then the response should be OK
        And  the response list should have "2" item(s)
        And  every item in the list should have available "False"

    Scenario: Availability filter accepts "1" as truthy
        When I search for products by availability "1"
        Then the response should be OK
        And  every item in the list should have available "True"

    Scenario: Availability filter accepts "0" as falsy
        When I search for products by availability "0"
        Then the response should be OK
        And  every item in the list should have available "False"


    ##################################################################
    # CREATE (baseline — verifies the Background data loads correctly)
    ##################################################################

    Scenario: Create a new product
        When I send a POST request to "/products" with body
          """
          {
              "name":        "Wrench",
              "description": "12-inch adjustable wrench",
              "price":       "18.99",
              "available":   true,
              "category":    "TOOLS"
          }
          """
        Then the response should be Created
        And  the response JSON field "name" should be "Wrench"
        And  the response JSON field "category" should be "TOOLS"

    Scenario: Create a product with missing fields returns 400
        When I send a POST request to "/products" with body
          """
          { "name": "Incomplete Product" }
          """
        Then the response status code should be "400"
