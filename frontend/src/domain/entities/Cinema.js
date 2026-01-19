/**
 * Cinema Entity - Domain Model
 * Represents a cinema in the business domain
 */
export class Cinema {
    constructor({
        id,
        name,
        location,
        email,
        phone,
        address,
        zipCode,
        rating
    }) {
        this.id = id;
        this.name = name;
        this.location = location;
        this.email = email;
        this.phone = phone;
        this.address = address;
        this.zipCode = zipCode;
        this.rating = rating;
    }
}
