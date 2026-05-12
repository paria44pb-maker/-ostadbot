# Simple in-memory chat history storage

user_histories = {}


def add_to_history(user_id: int, role: str, content: str):
    """
    Add a message to the user's chat history.
    """
    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({
        "role": role,
        "content": content
    })


def get_history(user_id: int):
    """
    Return the chat history for a user.
    """
    return user_histories.get(user_id, [])


def clear_history(user_id: int):
    """
    Remove all history for a specific user.
    """
    if user_id in user_histories:
        del user_histories[user_id]
