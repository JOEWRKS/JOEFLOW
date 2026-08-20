# Email service

`sendTransactionalEmail({templateKey, recipient, variables})` queues an email and returns a provider message ID. Queue acceptance does not guarantee delivery. The service emits delivered, bounced, and complained webhooks. Product behavior for those webhooks is not defined.
