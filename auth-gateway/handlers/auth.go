package handlers

import (
	"auth-gateway/utils"
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

	// Dummy auth check
	if creds.Username == "admin" && creds.Password == "password" {
		token, err := utils.GenerateJWT(creds.Username)
		if err != nil {
			http.Error(w, "Could not generate token", http.StatusInternalServerError)
			return
		}
		w.Write([]byte(token))
		return
	}
	http.Error(w, "Unauthorized", http.StatusUnauthorized)
}

func Protected(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Access granted to protected resource"))
}
