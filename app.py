from flask import Flask, render_template, request, redirect, url_for
import database

app = Flask(__name__)
database.create_database()

@app.route("/")
def index():
    items = database.get_all_items()
    return render_template("index.html", items=items)

@app.route("/items")
def items():
    all_items = database.get_all_items()
    return render_template("items.html", items=all_items)

@app.route("/item/<int:item_id>")
def item_detail(item_id):
    item = database.get_item_by_id(item_id)
    if item is None:
        return "Запис не знайдено", 404
    return render_template("item_detail.html", item=item)

@app.route("/search")
def search():
    query = request.args.get("query", "").strip()  # Змінили "q" на "query"
    results = []
    if query:
        database.add_search_history(query)
        results = database.search_items(query)
    return render_template("search.html", results=results, query=query)

@app.route("/history")
def history():
    history_records = database.get_search_history()
    return render_template("history.html", history=history_records)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

@app.route("/user/<username>")
def user_profile(username):
    status = request.args.get("status", "Новий гість")
    return render_template("user.html", username=username, status=status)

@app.route("/add", methods=["GET", "POST"])
def add():
    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        price_text = request.form.get("price", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not category:
            error = "Назва та категорія не можуть бути порожніми."
        else:
            try:
                price = float(price_text)
                database.add_menu_item(title, category, price, description)
                return redirect(url_for("index"))
            except ValueError:
                error = "Введено некоректне числове значення ціни."

    return render_template("add.html", error=error)

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    item = database.get_item_by_id(item_id)
    if item is None:
        return "Запис не знайдено", 404

    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        price_text = request.form.get("price", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            error = "Назва не може бути порожньою."
        else:
            try:
                price = float(price_text)
                database.update_item(item_id, title, category, price, description)
                return redirect(url_for("index"))
            except ValueError:
                error = "Неправильний формат ціни."

    return render_template("edit.html", item=item, error=error)

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    database.delete_item(item_id)
    return redirect(url_for("index"))

@app.route("/save", methods=["POST"])
def save_searched_item():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "Різне").strip()
    price_text = request.form.get("price", "0").strip()
    description = request.form.get("description", "").strip()

    try:
        price = float(price_text)
        database.add_menu_item(title, category, price, description)
    except ValueError:
        pass

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)