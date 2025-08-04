package utils

import (
	"crypto/rand"
	"encoding/base64"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

var jwtKey = []byte("your_super_secret_key") // Replace with env var in production

type CustomClaims struct {
	Role string `json:"role"`
	jwt.RegisteredClaims
}

func GenerateJWT(username, role string) (string, error) {
	claims := &CustomClaims{
		Role: role,
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   username,
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(15 * time.Minute)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtKey)
}

func ValidateJWT(tokenStr string) (*CustomClaims, error) {
	token, err := jwt.ParseWithClaims(tokenStr, &CustomClaims{}, func(token *jwt.Token) (interface{}, error) {
		return jwtKey, nil
	})
	if err != nil || !token.Valid {
		return nil, err
	}

	claims, ok := token.Claims.(*CustomClaims)
	if !ok {
		return nil, err
	}
	return claims, nil
}

func GenerateRefreshToken() string {
	b := make([]byte, 32)
	_, _ = rand.Read(b)
	return base64.URLEncoding.EncodeToString(b)
}


func BlacklistToken(token string, duration time.Duration) {
	rdb.Set(ctx, "bl:"+token, "revoked", duration)
}

func IsTokenBlacklisted(token string) bool {
	_, err := rdb.Get(ctx, "bl:"+token).Result()
	return err == nil
}