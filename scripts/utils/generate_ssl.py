from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
import uuid


async def generate_self_signed_certificate():
    # Генерация закрытого ключа RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Генерация случайного серийного номера для сертификата
    serial_number = int(uuid.uuid4())

    # Генерация случайных атрибутов для имени сертификата
    common_name = str(uuid.uuid4())

    # Генерация самоподписанного сертификата
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Mountain View"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"OpenAI"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    certificate = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        serial_number
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(common_name),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    # Создание уникальных имен для временных файлов ключа и сертификата
    key_filename = f"/var/folders/sq/c7pp9n5x4cxgjw5n5ppm4yk00000gn/T/{uuid.uuid4()}.key"
    cert_filename = f"/var/folders/sq/c7pp9n5x4cxgjw5n5ppm4yk00000gn/T/{uuid.uuid4()}.cert"

    # Сохранение закрытого ключа во временный файл
    with open(key_filename, "wb") as key_file:
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        key_file.write(private_key_pem)

    # Сохранение сертификата во временный файл
    with open(cert_filename, "wb") as cert_file:
        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
        cert_file.write(cert_pem)

    return key_filename, cert_filename