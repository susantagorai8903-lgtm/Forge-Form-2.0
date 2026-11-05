import asyncio

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import BlogCategory, Location, Program, ProgramCategory, Role

PROGRAMS = [
    (
        "Personal Training", "personal-training", "Personal Training",
        "A plan built around your life, your goals, and the way you want to feel.",
        "Work alongside a coach to build a thoughtful training routine around your starting point, schedule, and goals. Every session is personal, purposeful, and designed to help you keep showing up.",
        ["One-to-one coaching", "Personal fitness assessment", "Customized workout plan", "Progress check-ins"],
        "Anyone who values individual attention, whether new to training or ready for a fresh challenge.",
        "/images/personal%20tranning.jpg",
    ),
    (
        "Strength Training", "strength-training", "Strength Training",
        "Learn the lifts, build confidence, and get stronger at a pace that feels right.",
        "Develop strength with coached resistance training, functional movements, and a steady approach to progression. We focus on great technique and repeatable habits—not quick fixes.",
        ["Progressive strength work", "Resistance training", "Functional movement practice", "Technique coaching"],
        "Beginners learning the basics, as well as experienced lifters looking for more structure and coaching.",
        "/images/b1.jpeg",
    ),
    (
        "Weight Loss Coaching", "weight-loss", "Weight Loss",
        "Build consistent movement and everyday habits without all-or-nothing thinking.",
        "Create a supportive training routine focused on consistency, strength, and sustainable wellness habits. Nutrition guidance is educational and can complement—not replace—professional care.",
        ["Goal-oriented training plan", "Activity and habit tracking", "Regular coaching check-ins", "General nutrition education"],
        "People who want a supportive, practical approach to movement and long-term lifestyle change.",
        "/images/h3.jpeg",
    ),
    (
        "Mobility & Flexibility", "mobility", "Mobility & Flexibility",
        "Make room for better movement, thoughtful recovery, and a wider range of motion.",
        "Sessions blend mobility drills, flexibility routines, and controlled movement to help you move with intention. Your coach will adapt the work to your comfort and experience.",
        ["Mobility-focused sessions", "Flexibility routines", "Movement quality practice", "Recovery-minded coaching"],
        "Anyone who wants to give mobility and movement quality a more consistent place in their routine.",
        "/images/h9.jpeg",
    ),
    (
        "Nutrition Guidance", "nutrition-guidance", "Nutrition Guidance",
        "Practical, general education to help make food choices feel more approachable.",
        "Get general nutrition education and lifestyle guidance that supports your training goals. We keep it practical, non-prescriptive, and grounded in sustainable everyday habits.",
        ["General nutrition education", "Goal-oriented lifestyle support", "Habit-building ideas", "Coaching alongside your training"],
        "People looking for practical context and supportive habits to complement an active lifestyle.",
        "/images/nutrition%20guidance.jpg",
    ),
]
PROGRAM_CATEGORIES = ["Personal Training", "Strength Training", "Weight Loss", "Mobility & Flexibility", "Nutrition Guidance"]
BLOG_CATEGORIES = ["Strength Training", "Nutrition", "Personal Wellness", "Weight Management", "Mobility", "Fitness Tips"]


async def seed() -> None:
    async with SessionLocal() as session:
        async with session.begin():
            for role_name in ("SUPER_ADMIN", "ADMIN", "STAFF"):
                role = await session.scalar(select(Role).where(Role.name == role_name))
                if role is None:
                    session.add(Role(name=role_name))
            categories = {}
            for name in PROGRAM_CATEGORIES:
                category = await session.scalar(select(ProgramCategory).where(ProgramCategory.name == name))
                if category is None:
                    category = ProgramCategory(name=name, slug=name.lower().replace(" & ", "-").replace(" ", "-"))
                    session.add(category)
                    await session.flush()
                categories[name] = category
            for name, slug, category, summary, description, benefits, target_audience, image_url in PROGRAMS:
                exists = await session.scalar(select(Program).where(Program.slug == slug))
                if exists is None:
                    session.add(Program(
                        name=name, slug=slug, category_id=categories[category].id,
                        short_description=summary,
                        description=description,
                        benefits=benefits,
                        target_audience=target_audience,
                        image_url=image_url,
                        is_active=True,
                    ))
            for name in BLOG_CATEGORIES:
                exists = await session.scalar(select(BlogCategory).where(BlogCategory.name == name))
                if exists is None:
                    session.add(BlogCategory(name=name, slug=name.lower().replace(" ", "-")))
            location = await session.scalar(select(Location).where(Location.name == "Forge & Form Personal Training"))
            if location is None:
                session.add(Location(
                    name="Forge & Form Personal Training",
                    address="1900 Division Street",
                    city="Portland",
                    state="OR",
                    postal_code="97202",
                    country="USA",
                    phone="(503) 555-0139",
                    email="training@forgeandform.com",
                    opening_hours=None,
                    is_active=True,
                ))


if __name__ == "__main__":
    asyncio.run(seed())
