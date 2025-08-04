package main

import (
	"auth-gateway/handlers"
	"auth-gateway/middleware"
	"log"
	"net/http"
)

func main() {
	http.HandleFunc("/login", handlers.Login)
	http.Handle("/protected", middleware.AuthMiddleware(http.HandlerFunc(handlers.Protected)))

	log.Println("Auth Gateway running on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
