from pyngrok import ngrok

# Mở tunnel đến backend port 8000
public_url = ngrok.connect(8000)
print(f"✅ Public URL: {public_url.public_url}")

print("🚀 Tunnel đang chạy, đừng đóng cửa sổ này!")
print("➡️ Dán link này vào Unity config.json:")
print(f'{{ "baseUrl": "{public_url.public_url}" }}')

# Giữ tiến trình chạy để tunnel không đóng
input("\nNhấn ENTER để đóng tunnel...")
