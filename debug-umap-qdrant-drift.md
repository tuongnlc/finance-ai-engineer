# Debug Session: umap-qdrant-drift

Status: OPEN

## Symptom
- Vector `UMAP.transform(...)` tinh tay khac vector doc lai tu collection `newspaper_topic_modelling_embedded` sau khi load.

## Scope
- Files lien quan: `test_compare_space_dimension.py`, `src/applications/topic_modeling/inference/inference_umap.py`, `src/applications/topic_modeling/use_case/umap_inference.py`, `src/shared/data_pipeline/load/qdramt_loader.py`, `src/shared/data_pipeline/extract/qdrant_extractor.py`

## Initial Hypotheses
- H1: Vector ghi vao Qdrant khong phai dung gia tri `vector_umap` vua sinh ra.
- H2: Vector trong Qdrant bi thay doi do ep kieu/serialize khi upload va doc lai.
- H3: `id` giong nhau nhung mapping record giua manual path va load-back path van lech o mot buoc nao do.
- H4: `InferenceUMAPUseCase.load()` dang doc/ghi khac tap du lieu so voi tap du lieu manual test.
- H5: Co chenhlech do precision cua `float32`/`float64`, nhung muc chenhlech dang lon hon tolerance mac dinh cua `np.allclose`.

## Plan
- Them instrumentation de log id, shape, dtype, va mot vai vector mau truoc khi load va sau khi extract lai.
- Chay tai hien lai testcase.
- So sanh log de xac nhan vector bi khac o buoc nao dau tien.

## Evidence
- `manual transform snapshot`: `manual_vector_prefix = [11.279776573181152, 6.95720100402832, 6.855870246887207, 3.715968132019043, 9.796415328979492]`
- `pre-upload dataframe snapshot`: `sample_vector_prefix` giong het manual.
- `pointstruct snapshot before upload`: `first_point_vector_prefix` van giong het manual.
- `aligned compare snapshot`: `id_match = true`, nhung `qdrant_vector_prefix = [0.61866957, 0.38158634, 0.3760286, 0.20381224, 0.53731066]`, `max_abs_diff = 11.031334058361816`.
- Collection `newspaper_topic_modelling_embedded`: `VectorParams(size=5, distance=Cosine)`.
- Kiem tra so hoc: chuan hoa L2 cua vector manual cho ra `[0.6186696287677735, 0.3815863669373282, 0.3760286095210774, 0.2038122483928545, 0.5373106989764959]`, trung voi vector doc tu Qdrant.

## Hypothesis Status
- H1: REJECTED. Vector truoc upload dung gia tri `vector_umap`.
- H2: CONFIRMED. Qdrant thay doi vector theo co che normalize cua `Cosine`.
- H3: REJECTED. `id_match = true`.
- H4: REJECTED. Mau `id` va vector truoc upload trung voi manual path.
- H5: REJECTED. Sai khac khong phai precision nho; day la bien doi co he thong do normalize.

## Root Cause
- Collection dich duoc cau hinh `distance=Cosine`, nen Qdrant normalize vector ve unit norm khi luu/index. Vi vay vector doc lai khong con la raw output cua `UMAP.transform(...)`, ma la phien ban da duoc L2-normalize.
