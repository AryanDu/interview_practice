"""
Setup script for Interview Practice App
"""
import os
import subprocess
import sys

def create_directories():
    """Create necessary directories"""
    directories = [
        "data/vector_db",
        "templates/prompts",
        "jailbreak_results"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False
    return True

def verify_env_file():
    """Verify .env file exists"""
    if os.path.exists(".env"):
        print("✓ .env file found")
        return True
    else:
        print("⚠ .env file not found. Please create one with your API keys:")
        print("  OPENAI_API_KEY=your_key_here")
        print("  GOOGLE_API_KEY=your_key_here (optional)")
        print("  ANTHROPIC_API_KEY=your_key_here (optional)")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("Interview Practice App - Setup")
    print("=" * 50)
    
    create_directories()
    verify_env_file()
    
    install = input("\nInstall dependencies? (y/n): ").lower().strip()
    if install == 'y':
        install_dependencies()
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nTo run the app:")
    print("  streamlit run app.py")
    print("\nMake sure your .env file contains your API keys.")

if __name__ == "__main__":
    main()
