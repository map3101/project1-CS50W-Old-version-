# Project 1: Books
 
CS50's Web Programming with Python and JavaScript

## Description

This is a site where the user can register or log in to search books contained in the database. Once logged in the user will be redirected to a search page. After performing the search a results page will be shown. For each book the user can publish a review containing a rating from 1 to 5 and a written opnion. On the page of each book it is also possible to view the reviews left by other users.

**GoodReads API:** On each book page the rating count and average rating from GoosReads will be displayed(if available).

**API:** The user can make a GET request to /api/isbn, where isbn is an ISBN number. After doing this request the website will return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score.
