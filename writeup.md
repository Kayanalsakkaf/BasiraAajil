# Technical Write-Up (2 to 4 pages)

Explain your design, the tools or approaches you’d choose, and the reasoning behind them.

You may include pseudocode, YAML, or configuration snippets were helpful.

The challenge you have given is to evolve the Basira platform from a basic OCR service into a scalable, multi-model, auditable system. My research on Aajil.sa made assume the following:

* This system is required to carry essential ‘buy now pay later’ solutions and create applications for loans.
* High emphasis on security and regulation due the financial nature of business.
* Unlike large banking loans, budget should be taken into consideration.

The design considers four aspects, ensuring a production-grade system capable of processing thousands of documents daily while adhering to regulatory constraints.

# – Queue Stage:

S3 ObjectCreated event will be configured to place a message on an Amazon SQS (Simple Queue Service) queue which acts as a buffer in case of documents upload spike and supports at-least-once delivery. Messages will remain in the queue until the Step Function has pulled them successfully and started their processing. This ensures that no document upload is ever "lost" in case of transient failures. Dead-Letter Queue (DLQ). If a message (pointing to a document) fails processing repeatedly. For example, a corrupt file that causes the Step Function to fail consistently, SQS will automatically move this "poison pill" message to the DLQ after a set number of retries. The AWS Step Function is then triggered from - or more likely - polls - this queue for new messages. The SQS queue acts as an essential buffer. If multiple documents are uploaded at once - say, at the end of a month - they will queue up safely.

*The system core would be an event-driven workflow orchestrated by AWS Step Functions. This serverless-first approach was chosen after I carefully considered multiple factors of what your business might need and what I know from experience. I appreciate that you are not as my previous employer where significant budget was allocated to employees for one of the largest banking groups in the UK. We used Apache Airflow UI instead of MWAA on AWS. Although this was cheaper to them than MWAA and provided more control, we had a large, dedicated team to managing and debugging any issues with Airflow. The trade-off here is reallocating the cost that might be used for employees onto the serverless Step Function that will only cost per usage not all the time. According to ChatGPT, this equates to:*

***$26,665 / $0.000025 per transition =***

***1,066,600,000 transitions / 9 transitions per document =***

***118,511,111 documents per year.***

*Let’s say a team of 2-3 would cost 100,000+ ($26,665 ) SAR per year. If Aajil’s currently processes more 100+ million documents per year, then Airflow can replace Step Functions. Despite my reasoning, it is limited to my own assumption of what business decisions Aajil wishes to take for cost savings and the size of documents the company processes.*

# – Categorise Stage

We could create a custom classifier that Aajil will train on its own labelled data to recognise the specific document types before returning a JSON object. This output is passed back to the Step Function's state. It would be beneficial to have the pipeline diverge at this stage for each document type. For example, if the system identifies the document as a national ID, it will send it to a specified pipeline for IDs that will apply specific business and regulatory compliance rules.

*For a unique document that requires custom-made approach, custom entities can be added to comply. In addition, I believe this can be developed at a later stage to start incorporating ML models (See Section 2.5).*

# – Extract & Enrich Stage

This would be a branching stage that routes the document to specialised AI models based on its type as follow up from previous pipeline divisions. ***Comprehends PII detection*** feature can be configured to detect both universal PII such as credit card numbers, and country-specific PII such as Saudi national ID numbers. The system should not only detect PII but also redact it before storing it in the "Silver" layer. We could potentially use ***DetectPiiEntities*** API (in **AWS Comprehend**) to identify the PII and then apply a transformation. For our "Silver" layer, we will use the MaskMode option ***REPLACE\_WITH\_PII\_ENTITY\_TYPE***.

*This approach is superior to simple deletion as it satisfies the PDPL principle of confidentiality while retaining the structural information of the document. It allows data scientists to build models without ever being exposed to the PII itself. I also believe this would be critical for ensuring data privacy in a case where the AI extraction model showed low confidentiality score and required human review or there was a scenario where specific factors needed to be checked, and compliance does not allow for such. We had massive challenges in implementing testing for updates and versioning in pre-production at my previous job where we were not able to test with customer data and that is why it is essential to build systems with such compliances and modularity for future expansion of data privacy and protections.*

# – Validate and Lineage Stages

The AWS Step Function inherently tracks the state of each document's workflow which can pinpoint exactly where a document is in the process. A Lambda function runs business logic checks on the extracted data for requirements such as valid id format. Every significant action (ingestion, classification, extraction, validation) is logged. This Lambda function writes metadata to a DynamoDB table which serves as our audit log, tracking a document's document, its state, which model versions were used, and timestamps. This ensures full traceability . If validation fails or the extraction model returns a low confidence score, the Step Function routes the document for human review. Low confidence entities are flagged for manual checks.

# – Brief Reflections

*This system design is extensible, whether for adding a new custom-made document type or accommodating for both Arabic and English documents. A significant challenge in this kind of extensible approach is the fact financial documents and regulations are ever-changing. By the time we set a new custom-made document a new requirement could be enforced on businesses. A recent published paper explained there was significant ‘chaos’ of real-world documents. These were listed as:*

1. ***Schema Drift:*** *Different invoices use "Amount Due," "Total," or "Final Cost" for the same concept.*
2. ***Domain-Specific Reasoning****: Documents contain shorthand like "$8 \times 20^{\prime}$ CONTAINERS" 2 that requires inference, not just extraction.*
3. ***Format Variability:*** *Documents are a mix of digital-native files, half-legible scans, and photos3*

*The biggest long-term risk to my pipeline is "schema drift", which are new formats, layouts, and field names that may force the automation back to manual review. The paper makes a critical distinction between extraction and reasoning. My current design is strong at extraction, but it will fail if it encounters domain-specific logic. An example can be not knowing if certain numbers refer to centimetres, metres, or kilometres. The paper's proposed solution is to add an LLM. This shifts the problem from model retraining to prompt engineering. Specialised architectures like LayoutLMv3 "require a lot of labelled data" and are not "adaptable to different document formats for industry use". If I relied only on these, I would be trapped in an endless, expensive cycle of retraining. Another part of the solution could be Automatic Prompt Engineering (APE) to "dynamically define new fields and relationships without requiring retraining of the LLM". This makes the system "inherently modular" and scalable, which is essential for a production-grade system. The paper's baseline models (QA and DQA), which lack the reasoning capabilities of the full LLM pipeline, failed completely. They achieved a 0.000% Document Extraction Accuracy. This is why although my design for the current assessment does not incorporate it, I believe that Basira should and Aajil team should not consider LLM as a nice to have add on but something of high priority to develop for actual automation.*

![A screenshot of a computer  AI-generated content may be incorrect.](data:image/png;base64...)

# Implementation Sample (AI Generated – Pseudo)

{

"document\_id": "doc-uuid-12345",

"document\_type": "INVOICE",

"ingestion\_timestamp": "2025-11-14T18:00:00Z",

"status": "VALIDATED\_SUCCESS",

"source\_s3\_key": "s3://basira-bronze/uploads/doc-uuid-12345/original.pdf",

"validation\_rules\_passed": [

"total\_matches\_line\_items",

"vendor\_in\_registry"

],

"extracted\_data": {

"vendor\_name": "Example Tech Solutions",

"invoice\_number": "INV-2025-101",

"invoice\_date": "2025-11-01",

"due\_date": "2025-12-01",

"total\_amount": 1500.00,

"currency": "SAR",

"line\_items": [

{

"description": "Cloud Service Subscription",

"quantity": 1,

"unit\_price": 1000.00,

"total": 1000.00

},

{

"description": "Support Hours",

"quantity": 5,

"unit\_price": 100.00,

"total": 500.00

}

]

},

"lineage": {

"classification\_model\_version": "v1.2-comprehend",

"extraction\_model\_version": "textract-analyze-v3.0",

"validation\_lambda\_version": "arn:aws:lambda:us-east-1:xxx:function:validate-invoice:15",

"processed\_by\_execution": "arn:aws:states:us-east-1:xxx:execution:doc-proc-sfn:doc-proc-..."

}

}

This Python snippet demonstrates the queue-driven processing module . It's a conceptual "poller" (which would run as a Lambda function triggered by SQS) that reads from the queue, starts the Step Function execution, and deletes the message.

# Data Design / Schema Sketch

The Lineage DynamoDB table is the key to versioning the processing logic. By logging which model versions (classifier v1.0, extraction v2.0) were used for each document, you have a complete audit trail. This design allows new models or business rules to be added without disruption , as the lineage log will always reflect which version of the logic processed a specific document. The data design follows the "Bronze, Silver, Gold" medallion architecture. This shows how data on Basira could evolve from raw to analytics ready tables. All stored on S3/DynamoDB.