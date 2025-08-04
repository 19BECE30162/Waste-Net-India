package handlers

import (
	"auth-gateway/utils"
	"auth-gateway/utils/oauth"
	"auth-gateway/utils/storage"
	"encoding/json"
	"net/http"
)

type Credentials struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func Login(w http.ResponseWriter, r *http.Request) {
	var creds Credentials
	_ = json.NewDecoder(r.Body).Decode(&creds)

	// Dummy users with roles
	users := map[string]struct {
		Password string
		Role     string
	}{
		"admin": {"password", "admin"},
		"user":  {"123456", "user"},
	}

	user, ok := users[creds.Username]
	if !ok || user.Password != creds.Password {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	accessToken, err := utils.GenerateJWT(creds.Username, user.Role)
	if err != nil {
		http.Error(w, "Failed to create access token", http.StatusInternalServerError)
		return
	}
	refreshToken := utils.GenerateRefreshToken()
	storage.SaveRefreshToken(refreshToken, creds.Username)

	json.NewEncoder(w).Encode(map[string]string{
		"access_token":  accessToken,
		"refresh_token": refreshToken,
	})
}

func Refresh(w http.ResponseWriter, r *http.Request) {
	var req struct {
		RefreshToken string `json:"refresh_token"`
	}
	_ = json.NewDecoder(r.Body).Decode(&req)

	username, ok := storage.VerifyRefreshToken(req.RefreshToken)
	if !ok {
		http.Error(w, "Invalid refresh token", http.StatusUnauthorized)
		return
	}

	// Default role: user (or look up in DB)
	accessToken, err := utils.GenerateJWT(username, "user")
	if err != nil {
		http.Error(w, "Token generation failed", http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(map[string]string{
		"access_token": accessToken,
	})
}

func Protected(w http.ResponseWriter, r *http.Request) {
	username := r.Context().Value("username").(string)
	w.Write([]byte("Welcome, " + username + "! You accessed a protected route."))
}

func AdminOnly(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("You have admin access."))
}

func GoogleLogin(w http.ResponseWriter, r *http.Request) {
	state := "random_state" // Add CSRF protection in real apps
	url := oauth.GetGoogleLoginURL(state)
	http.Redirect(w, r, url, http.StatusTemporaryRedirect)
}

func GoogleCallback(w http.ResponseWriter, r *http.Request) {
	code := r.URL.Query().Get("code")
	token, err := oauth.ExchangeCodeForToken(code)
	if err != nil {
		http.Error(w, "OAuth token exchange failed", http.StatusUnauthorized)
		return
	}

	email, err := oauth.GetGoogleUserInfo(token)
	if err != nil {
		http.Error(w, "Could not get user info", http.StatusUnauthorized)
		return
	}

	jwt, err := utils.GenerateJWT(email, "user")
	if err != nil {
		http.Error(w, "Failed to create JWT", http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(map[string]string{
		"access_token": jwt,
	})
}

func Logout(w http.ResponseWriter, r *http.Request) {
	token := r.Header.Get("Authorization")
	token = strings.TrimPrefix(token, "Bearer ")
	utils.BlacklistToken(token, 15*time.Minute) // Match token TTL

	refresh := r.URL.Query().Get("refresh_token")
	storage.RevokeRefreshToken(refresh)

	w.Write([]byte("Logged out successfully"))
}