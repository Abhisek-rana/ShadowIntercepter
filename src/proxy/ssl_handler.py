import os
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

CERT_DIR = "certs"
CA_KEY_FILE = os.path.join(CERT_DIR, "ca.key")
CA_CERT_FILE = os.path.join(CERT_DIR, "ca.crt")
DOMAIN_CERT_DIR = os.path.join(CERT_DIR, "domains")


def ensure_ca():
    os.makedirs(CERT_DIR, exist_ok=True)

    if os.path.exists(CA_KEY_FILE) and os.path.exists(CA_CERT_FILE):
        print("[+] CA already exists, reusing it.")
        return

    print("[+] Generating new CA certificate...")

    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ShadowIntercepter"),
        x509.NameAttribute(NameOID.COMMON_NAME, "ShadowIntercepter Root CA"),
    ])

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    with open(CA_KEY_FILE, "wb") as f:
        f.write(ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open(CA_CERT_FILE, "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    print(f"[+] CA created: {CA_CERT_FILE}")
    print("[!] Is certificate ko apne browser mein 'trusted' ke roop mein install karna hoga.")


def _load_ca():
    with open(CA_KEY_FILE, "rb") as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None)
    with open(CA_CERT_FILE, "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())
    return ca_key, ca_cert


def get_cert_for_domain(domain: str):
    """
    Diye gaye domain ke liye fake certificate banata hai (CA se signed).
    Pehle se bana hai to reuse karta hai (cache).
    """
    os.makedirs(DOMAIN_CERT_DIR, exist_ok=True)

    safe_name = domain.replace("*", "wildcard")
    cert_path = os.path.join(DOMAIN_CERT_DIR, f"{safe_name}.crt")
    key_path = os.path.join(DOMAIN_CERT_DIR, f"{safe_name}.key")

    if os.path.exists(cert_path) and os.path.exists(key_path):
        return cert_path, key_path

    ca_key, ca_cert = _load_ca()

    domain_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])

    domain_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(domain_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(domain)]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    with open(key_path, "wb") as f:
        f.write(domain_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open(cert_path, "wb") as f:
        f.write(domain_cert.public_bytes(serialization.Encoding.PEM))

    return cert_path, key_path


if __name__ == "__main__":
    ensure_ca()
    cert, key = get_cert_for_domain("example.com")
    print(f"[+] Domain cert: {cert}")
    print(f"[+] Domain key: {key}")