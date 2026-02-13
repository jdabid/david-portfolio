"""
Profile domain models.
Represents the CV owner's personal info, skills, experience, and education.
"""

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import Base, TimestampMixin, UUIDMixin


class Profile(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "profiles"

    full_name: Mapped[str] = mapped_column(String(200))
    headline: Mapped[str] = mapped_column(String(300))
    summary: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(String(254))
    location: Mapped[str] = mapped_column(String(200), default="")
    github_url: Mapped[str] = mapped_column(String(500), default="")
    linkedin_url: Mapped[str] = mapped_column(String(500), default="")
    avatar_url: Mapped[str] = mapped_column(String(500), default="")

    skills: Mapped[list["Skill"]] = relationship(back_populates="profile", cascade="all, delete")
    experiences: Mapped[list["Experience"]] = relationship(
        back_populates="profile", cascade="all, delete"
    )
    educations: Mapped[list["Education"]] = relationship(
        back_populates="profile", cascade="all, delete"
    )


class Skill(UUIDMixin, Base):
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(100))  # Backend, DevOps, Frontend, Tools
    level: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    profile_id: Mapped[str] = mapped_column(
        String, nullable=False
    )

    profile: Mapped["Profile"] = relationship(back_populates="skills")


class Experience(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "experiences"

    company: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    start_date: Mapped[str] = mapped_column(String(10))  # YYYY-MM
    end_date: Mapped[str] = mapped_column(String(10), default="Present")
    profile_id: Mapped[str] = mapped_column(String, nullable=False)

    profile: Mapped["Profile"] = relationship(back_populates="experiences")


class Education(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "educations"

    institution: Mapped[str] = mapped_column(String(300))
    degree: Mapped[str] = mapped_column(String(300))
    field: Mapped[str] = mapped_column(String(200), default="")
    start_date: Mapped[str] = mapped_column(String(10))
    end_date: Mapped[str] = mapped_column(String(10), default="")
    profile_id: Mapped[str] = mapped_column(String, nullable=False)

    profile: Mapped["Profile"] = relationship(back_populates="educations")
