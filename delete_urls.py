from app import app, db, Link


urls_to_delete = [
    "https://www.flashscore.com.tr/",
    "https://www.hepsiburada.com/",
    "https://www.trendyol.com/"
]


with app.app_context():
    for url in urls_to_delete:
        link = Link.query.filter_by(original_url=url).first()
        if link:
            db.session.delete(link)
            print(f"Deleted: {url}")

    db.session.commit()
    print("All selected URLs deleted")



