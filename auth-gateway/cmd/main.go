package main

// Login godoc
// @Summary Login and receive JWT
// @Tags auth
// @Accept json
// @Produce json
// @Param credentials body handlers.Credentials true "Login credentials"
// @Success 200 {object} map[string]string
// @Failure 401 {string} string "Unauthorized"
// @Router /login [post]

import (
	"auth-gateway/handlers"
	"auth-gateway/middleware"
	"log"
	"net/http"
	"github.com/go-chi/chi/v5"
	// swagger "github.com/swaggo/http-swagger"
	// _ "auth-gateway/docs"
)

func main() {
	r := chi.NewRouter()

	r.Use(middleware.CorsMiddleware)

	r.Post("/login", handlers.Login)
	r.Post("/refresh", handlers.Refresh)
	r.Get("/auth/google", handlers.GoogleLogin)
	r.Get("/auth/google/callback", handlers.GoogleCallback)
	r.Post("/logout", handlers.Logout)

	r.Group(func(r chi.Router) {
		r.Use(middleware.AuthMiddleware)
		r.Get("/protected", handlers.Protected)
		r.With(middleware.RequireRole("admin")).Get("/admin", handlers.AdminOnly)
	})

	// r.Get("/swagger/*", swagger.WrapHandler)

	log.Println("Auth Gateway running on :8080")
	log.Fatal(http.ListenAndServe(":8080", r))
}
