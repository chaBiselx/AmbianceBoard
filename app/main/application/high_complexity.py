"""
Fichier avec complexité cyclomatique élevée pour démonstration SonarQube
"""


def complex_business_logic(user, product, order, payment, shipping):
    """
    Fonction avec une complexité cyclomatique très élevée
    """
    result = {
        'status': 'pending',
        'errors': [],
        'warnings': [],
        'total': 0
    }
    
    # Validation utilisateur (complexité +5)
    if user is None:
        result['errors'].append("User is required")
        return result
    else:
        if not user.get('is_active'):
            result['errors'].append("User is not active")
            return result
        else:
            if user.get('is_banned'):
                result['errors'].append("User is banned")
                return result
            else:
                if not user.get('email_verified'):
                    result['warnings'].append("Email not verified")
                else:
                    if user.get('account_type') == 'premium':
                        result['discount'] = 0.15
                    elif user.get('account_type') == 'gold':
                        result['discount'] = 0.10
                    elif user.get('account_type') == 'silver':
                        result['discount'] = 0.05
                    else:
                        result['discount'] = 0
    
    # Validation produit (complexité +8)
    if product is None:
        result['errors'].append("Product is required")
        return result
    else:
        if not product.get('available'):
            result['errors'].append("Product not available")
            return result
        else:
            if product.get('stock', 0) <= 0:
                result['errors'].append("Product out of stock")
                return result
            else:
                if product.get('category') == 'electronics':
                    if product.get('warranty_required'):
                        result['warranty_cost'] = product.get('price', 0) * 0.1
                    else:
                        result['warranty_cost'] = 0
                elif product.get('category') == 'clothing':
                    if product.get('size') not in ['S', 'M', 'L', 'XL']:
                        result['errors'].append("Invalid size")
                        return result
                elif product.get('category') == 'food':
                    if product.get('expiry_date'):
                        from datetime import datetime
                        if datetime.now() > product.get('expiry_date'):
                            result['errors'].append("Product expired")
                            return result
    
    # Validation commande (complexité +10)
    if order is None:
        result['errors'].append("Order is required")
        return result
    else:
        if order.get('quantity', 0) <= 0:
            result['errors'].append("Invalid quantity")
            return result
        else:
            if order.get('quantity') > product.get('stock', 0):
                result['errors'].append("Not enough stock")
                return result
            else:
                if order.get('quantity') > 10:
                    if order.get('bulk_order_approved'):
                        result['bulk_discount'] = 0.20
                    else:
                        result['warnings'].append("Bulk order requires approval")
                        result['bulk_discount'] = 0
                else:
                    if order.get('quantity') > 5:
                        result['bulk_discount'] = 0.10
                    elif order.get('quantity') > 3:
                        result['bulk_discount'] = 0.05
                    else:
                        result['bulk_discount'] = 0
    
    # Validation paiement (complexité +12)
    if payment is None:
        result['errors'].append("Payment is required")
        return result
    else:
        if payment.get('method') == 'credit_card':
            if not payment.get('card_number'):
                result['errors'].append("Card number required")
                return result
            elif len(payment.get('card_number', '')) != 16:
                result['errors'].append("Invalid card number")
                return result
            elif not payment.get('cvv'):
                result['errors'].append("CVV required")
                return result
            elif len(payment.get('cvv', '')) != 3:
                result['errors'].append("Invalid CVV")
                return result
            else:
                result['payment_fee'] = 0.03
        elif payment.get('method') == 'paypal':
            if not payment.get('paypal_email'):
                result['errors'].append("PayPal email required")
                return result
            else:
                result['payment_fee'] = 0.04
        elif payment.get('method') == 'bank_transfer':
            if not payment.get('iban'):
                result['errors'].append("IBAN required")
                return result
            elif len(payment.get('iban', '')) < 15:
                result['errors'].append("Invalid IBAN")
                return result
            else:
                result['payment_fee'] = 0.01
        elif payment.get('method') == 'cash':
            result['payment_fee'] = 0
        else:
            result['errors'].append("Invalid payment method")
            return result
    
    # Validation livraison (complexité +15)
    if shipping is None:
        result['errors'].append("Shipping is required")
        return result
    else:
        if shipping.get('country') == 'FR':
            if shipping.get('method') == 'express':
                result['shipping_cost'] = 15
                result['delivery_days'] = 1
            elif shipping.get('method') == 'standard':
                result['shipping_cost'] = 5
                result['delivery_days'] = 3
            elif shipping.get('method') == 'economy':
                result['shipping_cost'] = 2
                result['delivery_days'] = 7
            else:
                result['errors'].append("Invalid shipping method")
                return result
        elif shipping.get('country') == 'DE':
            if shipping.get('method') == 'express':
                result['shipping_cost'] = 20
                result['delivery_days'] = 2
            elif shipping.get('method') == 'standard':
                result['shipping_cost'] = 8
                result['delivery_days'] = 5
            elif shipping.get('method') == 'economy':
                result['shipping_cost'] = 4
                result['delivery_days'] = 10
            else:
                result['errors'].append("Invalid shipping method")
                return result
        elif shipping.get('country') in ['ES', 'IT', 'PT']:
            if shipping.get('method') == 'express':
                result['shipping_cost'] = 25
                result['delivery_days'] = 3
            elif shipping.get('method') == 'standard':
                result['shipping_cost'] = 10
                result['delivery_days'] = 7
            elif shipping.get('method') == 'economy':
                result['shipping_cost'] = 5
                result['delivery_days'] = 14
            else:
                result['errors'].append("Invalid shipping method")
                return result
        else:
            if shipping.get('international_shipping_enabled'):
                if shipping.get('method') == 'express':
                    result['shipping_cost'] = 50
                    result['delivery_days'] = 5
                elif shipping.get('method') == 'standard':
                    result['shipping_cost'] = 25
                    result['delivery_days'] = 14
                else:
                    result['errors'].append("Only express and standard available internationally")
                    return result
            else:
                result['errors'].append("International shipping not available")
                return result
    
    # Calcul final (complexité +5)
    if len(result['errors']) == 0:
        base_price = product.get('price', 0) * order.get('quantity', 0)
        
        if result.get('discount', 0) > 0:
            base_price = base_price * (1 - result['discount'])
        
        if result.get('bulk_discount', 0) > 0:
            base_price = base_price * (1 - result['bulk_discount'])
        
        total = base_price
        
        if result.get('warranty_cost', 0) > 0:
            total += result['warranty_cost']
        
        if result.get('payment_fee', 0) > 0:
            total += total * result['payment_fee']
        
        if result.get('shipping_cost', 0) > 0:
            total += result['shipping_cost']
        
        result['total'] = round(total, 2)
        result['status'] = 'success'
    else:
        result['status'] = 'error'
    
    return result


def nested_loops_example(data_matrix):
    """
    Fonction avec des boucles imbriquées (mauvaise performance)
    """
    result = []
    
    # 6 niveaux de boucles imbriquées !
    for i in range(len(data_matrix)):
        for j in range(len(data_matrix[i])):
            for k in range(len(data_matrix[i][j])):
                for m in range(len(data_matrix[i][j][k])):
                    for n in range(len(data_matrix[i][j][k][m])):
                        for p in range(len(data_matrix[i][j][k][m][n])):
                            value = data_matrix[i][j][k][m][n][p]
                            if value > 0:
                                if value % 2 == 0:
                                    if value > 100:
                                        result.append(value * 2)
                                    else:
                                        result.append(value)
                                else:
                                    if value > 50:
                                        result.append(value + 10)
                                    else:
                                        result.append(value - 5)
    
    return result
