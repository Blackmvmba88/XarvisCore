#!/usr/bin/env python3
"""
🏗️ Creative Forge - Asset Manager Core
Arquitectura Enterprise inspirada en Microsoft Azure Media Services

Principios:
1. Validate Early, Validate Often
2. Fail Fast with Clear Messages
3. Everything is Logged
4. State is Explicit

Arquitecto: Iyari Cancino Gomez
Fecha: 1 de Enero, 2026
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set, Any, Protocol
from pathlib import Path
from enum import Enum, auto
import hashlib
import magic  # python-magic for file type detection
import logging
from datetime import datetime
import json

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('creative_forge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# === ENUMS Y CONSTANTES ===

class AssetType(Enum):
    """Tipos de activos soportados"""
    VIDEO = auto()
    AUDIO = auto()
    IMAGE = auto()
    MODEL_3D = auto()
    SCENE = auto()
    TEXTURE = auto()
    UNKNOWN = auto()


class AssetStatus(Enum):
    """Estados del ciclo de vida de un activo"""
    PENDING_VALIDATION = auto()
    VALIDATED = auto()
    PROCESSING = auto()
    READY = auto()
    FAILED = auto()
    ARCHIVED = auto()


# Límites de seguridad
MAX_FILE_SIZE_MB = 5000  # 5GB
MIN_FILE_SIZE_BYTES = 100  # 100 bytes

# Extensiones permitidas por tipo
ALLOWED_EXTENSIONS: Dict[AssetType, Set[str]] = {
    AssetType.VIDEO: {'.mp4', '.mkv', '.mov', '.avi', '.webm', '.flv'},
    AssetType.AUDIO: {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'},
    AssetType.IMAGE: {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'},
    AssetType.MODEL_3D: {'.blend', '.fbx', '.obj', '.gltf', '.glb', '.stl'},
    AssetType.SCENE: {'.blend', '.ma', '.mb', '.max'},
    AssetType.TEXTURE: {'.jpg', '.png', '.exr', '.hdr', '.tga'}
}

# MIME types esperados
MIME_TYPES: Dict[AssetType, Set[str]] = {
    AssetType.VIDEO: {'video/mp4', 'video/x-matroska', 'video/quicktime', 'video/x-msvideo'},
    AssetType.AUDIO: {'audio/mpeg', 'audio/wav', 'audio/flac', 'audio/aac'},
    AssetType.IMAGE: {'image/jpeg', 'image/png', 'image/webp', 'image/tiff'},
}


# === MODELOS DE DATOS ===

@dataclass
class ValidationResult:
    """Resultado de validación con detalles completos"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, message: str) -> None:
        """Agregar error y marcar como inválido"""
        self.is_valid = False
        self.errors.append(message)
        logger.error(f"Validation error: {message}")
    
    def add_warning(self, message: str) -> None:
        """Agregar advertencia (no invalida)"""
        self.warnings.append(message)
        logger.warning(f"Validation warning: {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializar a diccionario"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata
        }


@dataclass
class Asset:
    """Representación de un activo digital"""
    id: str
    file_path: Path
    asset_type: AssetType
    status: AssetStatus
    checksum: str
    size_bytes: int
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'file_path': str(self.file_path),
            'asset_type': self.asset_type.name,
            'status': self.status.name,
            'checksum': self.checksum,
            'size_bytes': self.size_bytes,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


# === INTERFACES (PROTOCOLS) ===

class IValidator(Protocol):
    """Interface para validadores"""
    def validate(self, file_path: Path) -> ValidationResult:
        """Valida un archivo y retorna resultado detallado"""
        ...


class IMetadataExtractor(Protocol):
    """Interface para extractores de metadatos"""
    def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extrae metadatos de un archivo"""
        ...


# === VALIDADORES ===

class FileSystemValidator:
    """Validador de sistema de archivos"""
    
    @staticmethod
    def validate(file_path: Path) -> ValidationResult:
        """Valida existencia, permisos y propiedades básicas"""
        result = ValidationResult(is_valid=True)
        
        # 1. Verificar que existe
        if not file_path.exists():
            result.add_error(f"File does not exist: {file_path}")
            return result
        
        # 2. Verificar que es archivo (no directorio)
        if not file_path.is_file():
            result.add_error(f"Path is not a file: {file_path}")
            return result
        
        # 3. Verificar permisos de lectura
        if not file_path.stat().st_mode & 0o400:
            result.add_error(f"File is not readable: {file_path}")
            return result
        
        # 4. Verificar tamaño
        size_bytes = file_path.stat().st_size
        if size_bytes < MIN_FILE_SIZE_BYTES:
            result.add_error(f"File too small ({size_bytes} bytes, min: {MIN_FILE_SIZE_BYTES})")
        
        max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        if size_bytes > max_size_bytes:
            result.add_error(f"File too large ({size_bytes / (1024**2):.2f} MB, max: {MAX_FILE_SIZE_MB} MB)")
        
        result.metadata['size_bytes'] = size_bytes
        result.metadata['size_mb'] = round(size_bytes / (1024**2), 2)
        
        return result


class ExtensionValidator:
    """Validador de extensión de archivo"""
    
    @staticmethod
    def validate(file_path: Path, expected_type: Optional[AssetType] = None) -> ValidationResult:
        """Valida extensión contra tipos permitidos"""
        result = ValidationResult(is_valid=True)
        
        ext = file_path.suffix.lower()
        if not ext:
            result.add_error("File has no extension")
            return result
        
        # Si no se especifica tipo, buscar en todos
        if expected_type is None:
            found = False
            for asset_type, extensions in ALLOWED_EXTENSIONS.items():
                if ext in extensions:
                    result.metadata['detected_type'] = asset_type.name
                    found = True
                    break
            
            if not found:
                result.add_error(f"Unsupported file extension: {ext}")
        else:
            # Validar contra tipo específico
            allowed = ALLOWED_EXTENSIONS.get(expected_type, set())
            if ext not in allowed:
                result.add_error(f"Extension {ext} not allowed for {expected_type.name}")
                result.metadata['allowed_extensions'] = list(allowed)
        
        result.metadata['extension'] = ext
        return result


class MimeTypeValidator:
    """Validador de tipo MIME (magic number)"""
    
    @staticmethod
    def validate(file_path: Path, expected_type: Optional[AssetType] = None) -> ValidationResult:
        """Valida tipo MIME real del archivo"""
        result = ValidationResult(is_valid=True)
        
        try:
            # Detectar MIME type usando magic numbers
            mime = magic.from_file(str(file_path), mime=True)
            result.metadata['mime_type'] = mime
            
            if expected_type and expected_type in MIME_TYPES:
                allowed_mimes = MIME_TYPES[expected_type]
                if mime not in allowed_mimes:
                    result.add_warning(
                        f"MIME type {mime} not in expected types for {expected_type.name}: {allowed_mimes}"
                    )
            
        except Exception as e:
            result.add_error(f"Failed to detect MIME type: {e}")
        
        return result


class ChecksumValidator:
    """Validador de integridad mediante checksums"""
    
    @staticmethod
    def calculate_checksum(file_path: Path, algorithm: str = 'sha256') -> str:
        """Calcula checksum del archivo"""
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                # Leer en chunks para archivos grandes
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum: {e}")
            raise
    
    @staticmethod
    def validate(file_path: Path, expected_checksum: Optional[str] = None) -> ValidationResult:
        """Calcula y opcionalmente verifica checksum"""
        result = ValidationResult(is_valid=True)
        
        try:
            checksum = ChecksumValidator.calculate_checksum(file_path)
            result.metadata['checksum'] = checksum
            result.metadata['algorithm'] = 'sha256'
            
            if expected_checksum and checksum != expected_checksum:
                result.add_error(
                    f"Checksum mismatch: expected {expected_checksum}, got {checksum}"
                )
        except Exception as e:
            result.add_error(f"Checksum calculation failed: {e}")
        
        return result


# === ASSET MANAGER ===

class AssetManager:
    """Gestor centralizado de activos digitales"""
    
    def __init__(self, storage_root: Path):
        """
        Inicializa el gestor de activos
        
        Args:
            storage_root: Directorio raíz para almacenamiento
        """
        self.storage_root = storage_root.resolve()
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        # Índice de activos en memoria
        self.assets: Dict[str, Asset] = {}
        
        # Cargar índice si existe
        self._load_index()
        
        logger.info(f"✅ AssetManager initialized: {self.storage_root}")
    
    def _load_index(self) -> None:
        """Carga índice de activos desde disco"""
        index_file = self.storage_root / 'asset_index.json'
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    data = json.load(f)
                    # TODO: Deserializar activos
                    logger.info(f"📚 Loaded {len(data)} assets from index")
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
    
    def _save_index(self) -> None:
        """Guarda índice de activos a disco"""
        index_file = self.storage_root / 'asset_index.json'
        try:
            data = {aid: asset.to_dict() for aid, asset in self.assets.items()}
            with open(index_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 Saved {len(self.assets)} assets to index")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def validate_asset(
        self,
        file_path: Path,
        expected_type: Optional[AssetType] = None
    ) -> ValidationResult:
        """
        Valida un activo completamente
        
        Args:
            file_path: Ruta al archivo
            expected_type: Tipo esperado (opcional)
        
        Returns:
            ValidationResult con todos los detalles
        """
        logger.info(f"🔍 Validating asset: {file_path}")
        
        # Validación en cascada
        validators = [
            FileSystemValidator.validate(file_path),
            ExtensionValidator.validate(file_path, expected_type),
            MimeTypeValidator.validate(file_path, expected_type),
            ChecksumValidator.validate(file_path)
        ]
        
        # Consolidar resultados
        final_result = ValidationResult(is_valid=True)
        for result in validators:
            if not result.is_valid:
                final_result.is_valid = False
            final_result.errors.extend(result.errors)
            final_result.warnings.extend(result.warnings)
            final_result.metadata.update(result.metadata)
        
        if final_result.is_valid:
            logger.info(f"✅ Asset validated successfully: {file_path.name}")
        else:
            logger.error(f"❌ Asset validation failed: {file_path.name}")
            for error in final_result.errors:
                logger.error(f"  - {error}")
        
        return final_result
    
    def register_asset(
        self,
        file_path: Path,
        asset_type: AssetType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Asset]:
        """
        Registra un nuevo activo en el sistema
        
        Args:
            file_path: Ruta al archivo
            asset_type: Tipo de activo
            metadata: Metadatos adicionales
        
        Returns:
            Asset registrado o None si falla
        """
        # Validar primero
        validation = self.validate_asset(file_path, asset_type)
        if not validation.is_valid:
            logger.error(f"Cannot register invalid asset: {file_path}")
            return None
        
        # Crear objeto Asset
        asset_id = validation.metadata['checksum'][:16]  # Primeros 16 chars del hash
        
        asset = Asset(
            id=asset_id,
            file_path=file_path,
            asset_type=asset_type,
            status=AssetStatus.VALIDATED,
            checksum=validation.metadata['checksum'],
            size_bytes=validation.metadata['size_bytes'],
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        # Agregar metadatos de validación
        asset.metadata.update(validation.metadata)
        
        # Registrar
        self.assets[asset_id] = asset
        self._save_index()
        
        logger.info(f"✅ Asset registered: {asset_id} ({file_path.name})")
        return asset
    
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Obtiene activo por ID"""
        return self.assets.get(asset_id)
    
    def list_assets(
        self,
        asset_type: Optional[AssetType] = None,
        status: Optional[AssetStatus] = None
    ) -> List[Asset]:
        """Lista activos con filtros opcionales"""
        assets = list(self.assets.values())
        
        if asset_type:
            assets = [a for a in assets if a.asset_type == asset_type]
        
        if status:
            assets = [a for a in assets if a.status == status]
        
        return assets


# === TESTING ===

if __name__ == '__main__':
    # Ejemplo de uso
    manager = AssetManager(Path('./assets'))
    
    # Simular validación de archivo
    test_file = Path(__file__)  # Este mismo archivo como prueba
    result = manager.validate_asset(test_file)
    
    print("\n" + "="*60)
    print("VALIDATION RESULT")
    print("="*60)
    print(f"Valid: {result.is_valid}")
    print(f"\nErrors ({len(result.errors)}):")
    for err in result.errors:
        print(f"  ❌ {err}")
    print(f"\nWarnings ({len(result.warnings)}):")
    for warn in result.warnings:
        print(f"  ⚠️  {warn}")
    print(f"\nMetadata:")
    for key, value in result.metadata.items():
        print(f"  {key}: {value}")
    print("="*60)
