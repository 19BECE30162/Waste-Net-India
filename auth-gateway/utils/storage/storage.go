package storage
import (
	"context"
	"os"
	"time"

	"github.com/redis/go-redis/v9"
)

var (
	ctx = context.Background()
	rdb = redis.NewClient(&redis.Options{
		Addr:     os.Getenv("REDIS_ADDR"),     // e.g. redis:6379
		Password: os.Getenv("REDIS_PASSWORD"), // optional
		DB:       0,
	})
)

func SaveRefreshToken(token, username string) {
	rdb.Set(ctx, "refresh:"+token, username, 24*time.Hour)
}

func VerifyRefreshToken(token string) (string, bool) {
	val, err := rdb.Get(ctx, "refresh:"+token).Result()
	if err != nil {
		return "", false
	}
	return val, true
}

func RevokeRefreshToken(token string) {
	rdb.Del(ctx, "refresh:"+token)
}

func SaveUser(username, password string) {
	rdb.HSet(ctx, "users", username, password)
}

func GetUserPassword(username string) (string, bool) {
	pass, err := rdb.HGet(ctx, "users", username).Result()
	if err != nil {
		return "", false
	}
	return pass, true
}
