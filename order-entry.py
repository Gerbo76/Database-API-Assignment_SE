
from database import (
    get_customers,
    get_products,
    save_order,
    get_order
)
from datetime import date
from decimal import Decimal


# 1. Display customers and products
def display_customers(customers):
    print("\nCUSTOMERS")
    print(f"{'ID':<10}{'Name':<25}")
    print("-" * 35)

    for customer in customers:
        print(
            f"{customer['customer_id']:<10}"
            f"{customer['name']:<25}"
        )


def display_products(products):
    print("\nPRODUCTS")
    print(f"{'ID':<10}{'Product':<25}{'Price':>10}")
    print("-" * 45)

    for product in products:
        price = Decimal(str(product["price"]))
        print(
            f"{product['product_id']:<10}"
            f"{product['product_name']:<25}"
            f"${price:>9.2f}"
        )


# 2. Collect and validate user input
def get_valid_number(prompt, valid_ids=None):
    while True:
        try:
            number = int(input(prompt))

            if number <= 0:
                print("Please enter a positive whole number.")
                continue

            if valid_ids is not None and number not in valid_ids:
                print("ID not found. Please try again.")
                continue

            return number

        except ValueError:
            print("Invalid input. Please enter a whole number.")


# 3. Display order summary and confirm purchase
def confirm_order(customer, product, quantity):
    price = Decimal(str(product["price"]))
    total = price * quantity

    print("\nORDER SUMMARY")
    print("-" * 35)
    print("Customer:", customer["name"])
    print("Product:", product["product_name"])
    print("Quantity:", quantity)
    print(f"Unit Price: ${price:.2f}")
    print(f"Order Total: ${total:.2f}")
    print("-" * 35)

    while True:
        answer = input("Confirm order? (Y/N): ").strip().upper()

        if answer == "Y":
            return True

        elif answer == "N":
            return False

        else:
            print("Please enter Y or N.")


# 4. Display the order retrieved from Supabase
def display_saved_order(order, customers, products):
    customer = next(
        c for c in customers
        if c["customer_id"] == order["customer_id"]
    )

    product = next(
        p for p in products
        if p["product_id"] == order["product_id"]
    )

    price = Decimal(str(order["unit_price"]))
    total = price * order["quantity"]

    print("\nVERIFIED SAVED ORDER")

    print(
        f"{'Order ID':<10}"
        f"{'Customer':<18}"
        f"{'Product':<18}"
        f"{'Qty':<6}"
        f"{'Unit Price':<13}"
        f"{'Total':<12}"
        f"{'Date':<12}"
    )

    print("-" * 89)

    print(
        f"{order['order_id']:<10}"
        f"{customer['name']:<18}"
        f"{product['product_name']:<18}"
        f"{order['quantity']:<6}"
        f"${price:<12.2f}"
        f"${total:<11.2f}"
        f"{order['order_date']:<12}"
    )


  # Retrieve customer and product data
def main():
    try:
        customers = get_customers()
        products = get_products()

    except Exception:
        print("Unable to retrieve data from Supabase.")
        print("Check your connection and credentials.")
        return

    if not customers or not products:
        print("No customers or products available.")
        return

    # Display existing records
    display_customers(customers)
    display_products(products)

    # Create sets of valid IDs
    customer_ids = {
        c["customer_id"] for c in customers
    }

    product_ids = {
        p["product_id"] for p in products
    }

    # Ask for inputs
    customer_id = get_valid_number(
        "\nEnter customer ID: ",
        customer_ids
    )

    product_id = get_valid_number(
        "Enter product ID: ",
        product_ids
    )

    quantity = get_valid_number(
        "Enter quantity: "
    )

    # Find selected customer and product
    customer = next(
        c for c in customers
        if c["customer_id"] == customer_id
    )

    product = next(
        p for p in products
        if p["product_id"] == product_id
    )

    # Ask user to confirm order
    if not confirm_order(customer, product, quantity):
        print("Order canceled. Nothing was saved.")
        return

    # Prepare order data
    order = {
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "order_date": date.today().isoformat(),
        "unit_price": str(product["price"])
    }

    # Insert order into Supabase
    try:
        inserted = save_order(order)

        if not inserted or "order_id" not in inserted[0]:
            print("Order insertion could not be confirmed.")
            return

        order_id = inserted[0]["order_id"]

        print("\nOrder saved successfully!")
        print("Generated Order ID:", order_id)

    except Exception:
        print("Unable to confirm that the order was saved.")
        print("Check Supabase before trying again.")
        return

    # Query Supabase again to verify insertion
    try:
        saved = get_order(order_id)

        if not saved:
            print("Verification could not be completed.")
            print("No matching order was returned.")
            return

        display_saved_order(
            saved[0],
            customers,
            products
        )

    except Exception:
        print("Order was inserted, but verification failed.")
        print("Do not automatically insert the order again.")


# Run the program
if __name__ == "__main__":
    main()
