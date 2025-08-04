package middleware

import (
	"context"
	"net/http"
	"strings"

	"auth-gateway/utils"
)

if utils.IsTokenBlacklisted(token) {
	http.Error(w, "Token revoked", http.StatusUnauthorized)
	return
}
func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		auth := r.Header.Get("Authorization")
		if auth == "" || !strings.HasPrefix(auth, "Bearer ") {
			http.Error(w, "Missing or invalid token", http.StatusUnauthorized)
			return
		}

		token := strings.TrimPrefix(auth, "Bearer ")
		claims, err := utils.ValidateJWT(token)
		if err != nil {
			http.Error(w, "Invalid or expired token", http.StatusUnauthorized)
			return
		}

		ctx := context.WithValue(r.Context(), "username", claims.Subject)
		ctx = context.WithValue(ctx, "role", claims.Role)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func RequireRole(requiredRole string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			role, ok := r.Context().Value("role").(string)
			if !ok || role != requiredRole {
				http.Error(w, "Forbidden: requires "+requiredRole+" role", http.StatusForbidden)
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}
