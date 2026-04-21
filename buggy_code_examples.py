# Some buggy code examples I wrote while learning
# These don't work perfectly but show my learning process

def broken_triage_function(patient_data):
    """This function has bugs but I'm still learning"""
    # This doesn't handle missing data well
    if patient_data['heart_rate'] > 100:
        return 2
    elif patient_data['temperature'] > 38:
        return 3
    else:
        return 4  # This is too simplistic

def messy_websocket_handler(websocket):
    """WebSocket handler that sometimes breaks"""
    try:
        # This is probably not the right way to do this
        while True:
            data = websocket.receive()
            # Process data here
            websocket.send("OK")
    except:
        # Just ignore errors for now
        pass

def inefficient_data_loading():
    """This loads data inefficiently but it works"""
    data = []
    for i in range(1000):
        # This is slow but I don't know how to make it faster
        row = load_single_row(i)
        data.append(row)
    return data

def hardcoded_config():
    """Hardcoded values - not good practice but it works"""
    MODEL_PATH = "/home/user/models/llama"  # Hardcoded path
    DATABASE_URL = "sqlite:///./data.db"   # Hardcoded database
    MAX_PATIENTS = 50                      # Hardcoded limit
    
    return MODEL_PATH, DATABASE_URL, MAX_PATIENTS

def simple_error_handling():
    """Basic error handling - not comprehensive"""
    try:
        result = risky_operation()
        return result
    except:
        return None  # Just return None if anything goes wrong

# TODO: Fix all these functions
# TODO: Learn better error handling
# TODO: Make data loading more efficient
# TODO: Use proper configuration management



