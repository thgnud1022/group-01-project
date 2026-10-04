"""
Pydantic Schemas for AI Service Structured Input/Output Validation (TASK-009 / HD-03).
Enforces strict schema validation for LLM responses and fallback decision support.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class PRItemSchema(BaseModel):
    itemName: str = Field(..., description="Tên danh mục hoặc thiết bị được chuẩn hóa")
    quantity: int = Field(default=1, ge=1, description="Số lượng ước tính, nguyên dương >= 1")
    estimatedUnitPrice: float = Field(default=0.0, ge=0.0, description="Đơn giá ước tính (VND)")


class StandardizeRequest(BaseModel):
    raw_text: str = Field(..., min_length=1, description="Mô tả thô của người dùng khi tạo PR")


class StandardizeResponseSchema(BaseModel):
    title: str = Field(..., description="Tiêu đề chuẩn hóa cho Purchase Request")
    items: List[PRItemSchema] = Field(default_factory=list, description="Danh sách các hạng mục bóc tách")
    total_estimated_value: float = Field(default=0.0, ge=0.0, description="Tổng giá trị ước tính (VND)")
    is_fallback: bool = Field(default=False, description="Cờ đánh dấu kết quả được sinh từ Fallback Regex")
    fallback_reason: Optional[str] = Field(default=None, description="Lý do kích hoạt fallback (nếu có)")
    latency_seconds: float = Field(default=0.0, ge=0.0, description="Thời gian xử lý")
    grounded_sources: List[str] = Field(default_factory=list, description="Căn cứ hoặc quy tắc đối chiếu")


class QuotationInputItem(BaseModel):
    quotation_id: str
    supplier_name: str
    total_amount: float = Field(..., ge=0.0)
    unit_price: float = Field(..., ge=0.0)
    quantity: int = Field(default=1, ge=1)
    delivery_days: int = Field(default=0, ge=0)
    warranty_terms: Optional[str] = None
    valid_until: Optional[str] = None
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None
    is_expired: bool = False


class QuotationRecommendationRequest(BaseModel):
    purchase_request_id: str = Field(..., description="Mã Purchase Request cần đối soát")
    pr_title: Optional[str] = Field(default=None, description="Tiêu đề PR để cung cấp ngữ cảnh")
    quotations: Optional[List[QuotationInputItem]] = Field(default=None, description="Danh sách các báo giá")


class QuotationRankingItem(BaseModel):
    quotation_id: str
    supplier_name: str
    rank: int = Field(..., ge=1, description="Thứ hạng đề xuất (1 là tốt nhất)")
    score: float = Field(..., ge=0.0, le=100.0, description="Điểm đánh giá tổng hợp trên thang 100")
    pros: List[str] = Field(default_factory=list, description="Các điểm mạnh (giá, giao nhanh, bảo hành)")
    cons: List[str] = Field(default_factory=list, description="Các điểm yếu hoặc rủi ro")
    price_score: Optional[float] = Field(default=None, description="Điểm thành phần về giá (0-100)")
    lead_time_score: Optional[float] = Field(default=None, description="Điểm thành phần thời gian giao hàng (0-100)")
    reliability_score: Optional[float] = Field(default=None, description="Điểm thành phần độ tin cậy (0-100)")
    terms_score: Optional[float] = Field(default=None, description="Điểm thành phần điều khoản thương mại (0-100)")


class QuotationRecommendationResponse(BaseModel):
    purchase_request_id: str
    recommended_quotation_id: Optional[str] = Field(default=None, description="Mã báo giá được khuyến nghị lựa chọn")
    recommended_supplier_name: Optional[str] = Field(default=None, description="Tên nhà cung cấp được khuyến nghị")
    reasoning: str = Field(..., description="Lý do chi tiết giải thích cho đề xuất của AI")
    rankings: List[QuotationRankingItem] = Field(default_factory=list, description="Bảng xếp hạng chi tiết các báo giá")
    is_fallback: bool = Field(default=False, description="Cờ đánh dấu kết quả được sinh từ Fallback Heuristic")
    fallback_reason: Optional[str] = Field(default=None, description="Lý do kích hoạt fallback (nếu có)")
    confidence: float = Field(default=78.0, description="Độ tin cậy của đánh giá (%)")
    why: List[str] = Field(default_factory=list, description="Các luận điểm chính tại sao đề xuất nhà cung cấp này")
    risks: List[str] = Field(default_factory=list, description="Các rủi ro cần lưu ý")
    missing_data: List[str] = Field(default_factory=list, description="Dữ liệu còn thiếu cần làm rõ")
    anomalies: List[str] = Field(default_factory=list, description="Cảnh báo bất thường từ dữ liệu so sánh")

