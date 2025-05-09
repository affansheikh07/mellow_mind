# Use PHP with Apache
FROM php:8.2-apache

# Set working directory inside container
WORKDIR /var/www/html

# Copy project files into the working directory
COPY . .

# Set permissions (optional)
RUN chown -R www-data:www-data /var/www/html

# Enable Apache mod_rewrite (useful if you're using URL rewriting)
RUN a2enmod rewrite

# Optional: Install common PHP extensions (uncomment as needed)
# RUN docker-php-ext-install mysqli pdo pdo_mysql

# Expose port 80
EXPOSE 80
