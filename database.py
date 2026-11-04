from config import supabase

def get_customers():
    response = supabase.table("customers").select("*").execute()
    return response.data

def get_products():
    response = supabase.table("products").select("*").execute()
    return response.data

def save_order(order):
    response = supabase.table("orders").insert(order).execute()
    return response.data

def get_order(order_id):
    response = supabase.table("orders").select("*").eq(
        "order_id", order_id
    ).execute()
    return response.data