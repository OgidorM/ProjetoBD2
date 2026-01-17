/**
 * Cinema Entity - Domain Model
 * Represents a cinema in the business domain
 */
export class Cinema {
    constructor({
        id,
        name,
        location
    }) {
        this.id = id;
        this.name = name;
        this.location = location;
    }
}
