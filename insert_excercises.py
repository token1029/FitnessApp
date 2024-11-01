from apps import App
app = App()
mongo = app.mongo

def coaching_videos():
    """Define exercise data for various specializations"""
    exercise_data = [
        # Yoga exercises (from your existing list)
        {
            "specialization": "yoga",
            "exercise_id": 1,
            "image": "../static/img/yoga.jpg",
            "video_link": "https://www.youtube.com/watch?v=c8hjhRqIwHE",
            "name": "Yoga for Beginners",
            "description": "New to Yoga? Learn easy yoga poses to build strength, flexibility, and mental clarity.",
            "href": "yoga"
        },
        # Strength exercises
        {
            "specialization": "strength",
            "exercise_id": 2,
            "image": "../static/img/strength1.jpg",
            "video_link": "https://www.youtube.com/watch?v=8zWDuWKdBZU",
            "name": "Strength Workout 1",
            "description": "Intense strength training for muscle growth.",
            "href": "strength1"
        },
        {
            "specialization": "strength",
            "exercise_id": 3,
            "image": "../static/img/strength2.jpg",
            "video_link": "https://www.youtube.com/watch?v=DXL18E7QRbk",
            "name": "Strength Workout 2",
            "description": "Powerful strength workout for core and arms.",
            "href": "strength2"
        },
        {
            "specialization": "strength",
            "exercise_id": 4,
            "image": "../static/img/strength3.jpg",
            "video_link": "https://www.youtube.com/watch?v=21lYP86dHW4",
            "name": "Strength Workout 3",
            "description": "Full-body strength routine to build endurance.",
            "href": "strength3"
        },
        {
            "specialization": "strength",
            "exercise_id": 5,
            "image": "../static/img/strength4.jpg",
            "video_link": "https://www.youtube.com/watch?v=GNO4OtYoCYk",
            "name": "Strength Workout 4",
            "description": "Strengthen your core and lower body.",
            "href": "strength4"
        },
        # Cardio exercises
        {
            "specialization": "cardio",
            "exercise_id": 6,
            "image": "../static/img/cardio1.jpg",
            "video_link": "https://www.youtube.com/watch?v=yWnacRo2VbA",
            "name": "Cardio Blast",
            "description": "Get your heart pumping with this cardio workout.",
            "href": "cardio1"
        },
        {
            "specialization": "cardio",
            "exercise_id": 7,
            "image": "../static/img/cardio2.jpg",
            "video_link": "https://www.youtube.com/watch?v=crPb62o-z_E",
            "name": "High-Intensity Cardio",
            "description": "A high-intensity workout to burn calories fast.",
            "href": "cardio2"
        },
        {
            "specialization": "cardio",
            "exercise_id": 8,
            "image": "../static/img/cardio3.jpg",
            "video_link": "https://www.youtube.com/watch?v=kZDvg92tTMc",
            "name": "Cardio Circuit",
            "description": "Cardio circuit for endurance and speed.",
            "href": "cardio3"
        },
        {
            "specialization": "cardio",
            "exercise_id": 9,
            "image": "../static/img/cardio4.jpg",
            "video_link": "https://www.youtube.com/watch?v=M0uO8X3_tEA",
            "name": "Ultimate Cardio",
            "description": "Ultimate cardio routine for fat burning.",
            "href": "cardio4"
        },
        # CrossFit exercises
        {
            "specialization": "crossfit",
            "exercise_id": 10,
            "image": "../static/img/crossfit1.jpg",
            "video_link": "https://www.youtube.com/watch?v=D7lRZOCJEFw",
            "name": "CrossFit Starter",
            "description": "Beginner CrossFit workout to improve strength and conditioning.",
            "href": "crossfit1"
        },
        # Nutrition coaching videos
        {
            "specialization": "nutrition",
            "exercise_id": 11,
            "image": "../static/img/nutrition1.jpg",
            "video_link": "https://www.youtube.com/watch?v=8BKbu_s8p1Q&t=441s",
            "name": "Nutrition Basics",
            "description": "Learn the basics of nutrition for a healthier lifestyle.",
            "href": "nutrition1"
        },
        {
            "specialization": "nutrition",
            "exercise_id": 12,
            "image": "../static/img/nutrition2.jpg",
            "video_link": "https://www.youtube.com/watch?v=osqvOUJjaCo",
            "name": "Advanced Nutrition",
            "description": "Advanced tips for balanced nutrition.",
            "href": "nutrition2"
        },
        {
            "specialization": "nutrition",
            "exercise_id": 13,
            "image": "../static/img/nutrition3.jpg",
            "video_link": "https://www.youtube.com/watch?v=6cPvi21GhU8",
            "name": "Healthy Eating",
            "description": "Guide to healthy eating habits.",
            "href": "nutrition3"
        },
        {
            "specialization": "nutrition",
            "exercise_id": 14,
            "image": "../static/img/nutrition4.jpg",
            "video_link": "https://www.youtube.com/watch?v=dgj9aDIMPEs",
            "name": "Diet Planning",
            "description": "How to create a personalized diet plan.",
            "href": "nutrition4"
        }
    ]

    # Insert each exercise into the "exercises" collection
    collection = mongo.db["coaching_data"]

    for exercise in exercise_data:
        query = {"exercise_id": exercise["exercise_id"]}
        update = {"$set": exercise}
        collection.update_one(query, update, upsert=True)

