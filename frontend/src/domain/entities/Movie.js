/**
 * Movie Entity - Domain Model
 * Represents a movie in the business domain
 */
export class Movie {
    constructor({
        id,
        title,
        year,
        director,
        description,
        duration,
        category,
        rating,
        releaseDate,
        language,
        cinema,
        ageRating,
    }) {
        this.id = id;
        this.title = title;
        this.year = year;
        this.director = director;
        this.description = description;
        this.duration = duration;
        this.category = category;
        this.rating = rating;
        this.releaseDate = releaseDate;
        this.language = language;
        this.cinema = cinema;
        this.ageRating = ageRating;
    }

    /**
     * Get formatted duration as hours and minutes
     */
    getFormattedDuration() {
        if (!this.duration) return 'N/A';
        const hours = Math.floor(this.duration / 60);
        const minutes = this.duration % 60;
        return hours > 0 ? `${hours}h ${minutes}min` : `${minutes}min`;
    }

    /**
     * Get rating stars
     */
    getRatingStars() {
        return '⭐'.repeat(Math.round(this.rating));
    }
}

