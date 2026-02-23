---
title: "Top Infrastructure as Code Examples to Streamline Your Projects"
date: '2025-08-16'
description: "Discover 8 practical infrastructure as code examples with Terraform, AWS CloudFormation, Ansible, and more. Boost your automation skills today!"
draft: false
slug: '/infrastructure-as-code-examples'
tags:

  - infrastructure-as-code-examples
  - IaC-tools
  - DevOps-automation
  - Terraform-examples
  - CloudFormation-templates
images_fixed: true
---

![Article Header Image](https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts/infrastructure-as-code-examples/featured-image-be2560dd-1f85-415c-b05f-74da86d6b336.jpg)

Transitioning from manual infrastructure management to automated, version-controlled code is a game-changer for any engineering team. It introduces consistency, speed, and reliability into provisioning and managing complex systems. This guide moves beyond theory to provide a curated collection of practical **infrastructure as code examples**, breaking down not just the "what" but the strategic "why" behind each one.

We will dissect replicable code snippets and configurations for the industry's most essential tools. You'll gain tactical insights and actionable takeaways for implementing solutions with Terraform, Ansible, Pulumi, Kubernetes, and native cloud provider tools like AWS CloudFormation and Azure Resource Manager.

Whether you are a DevOps veteran refining your workflows or a developer just beginning your automation journey, these examples are designed to be immediately useful. They will equip you with the strategic understanding needed to build scalable, resilient, and efficient cloud environments. Each example serves as a blueprint for improving your own deployment pipelines, reducing manual errors, and accelerating your delivery lifecycle. Let's dive into the code that builds the cloud.

## 1. Terraform: The Cloud-Agnostic Standard

Terraform, an open-source tool from HashiCorp, has become the de facto standard for cloud-agnostic Infrastructure as Code (IaC). It uses a declarative configuration language called HCL (HashiCorp Configuration Language) to define the desired state of your infrastructure. Terraform then creates an execution plan to reach that state and provisions resources across various cloud providers like AWS, Azure, and Google Cloud, as well as other platforms.

This provider-agnostic approach is its primary strength. A team can use a consistent workflow and skillset to manage resources across a multi-cloud or hybrid-cloud environment. This avoids vendor lock-in and simplifies complex deployments. Terraform maintains a state file that maps real-world resources to your configuration, allowing it to manage and update infrastructure with precision.

### Strategic Breakdown

Terraform excels at managing complex, interdependent infrastructure. For example, you can define a virtual private cloud (VPC), subnets, security groups, and the virtual machines that reside within them all in a single set of configuration files. This makes it a powerful choice among **infrastructure as code examples** for building entire application environments from the ground up.

> **Key Insight:** Terraform's greatest advantage is its provider model. By abstracting the specific API calls for each cloud provider into reusable modules, it allows engineers to focus on the architecture's "what" rather than the provider's "how".

### Actionable Takeaways

* **Start with Modules:** Don't write everything from scratch. Leverage the extensive Terraform Registry for pre-built modules to accelerate development and ensure you follow best practices.
* **Manage State Remotely:** For team collaboration, always configure a remote backend (like an AWS S3 bucket or Terraform Cloud). This prevents state file conflicts and provides a single source of truth for your infrastructure's state.
* **Plan and Apply:** Always run `terraform plan` to review proposed changes before executing them with `terraform apply`. This simple step prevents accidental deletions or unintended modifications to critical resources.

## 2. AWS CloudFormation: The Native AWS Solution

AWS CloudFormation is Amazon's native Infrastructure as Code (IaC) service, allowing you to model, provision, and manage AWS resources using templates written in JSON or YAML. It functions as a single source of truth for your AWS environment. You define your desired state in a template, and CloudFormation handles the provisioning and configuration of resources in the correct order with dependency management.

![AWS CloudFormation](https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts/infrastructure-as-code-examples/0ca993cd-5437-4165-88a7-79dff7d54a62.jpg)

This deep integration with the AWS ecosystem is its core advantage. CloudFormation supports nearly all AWS services, often on day one of their release. It also includes features like automatic rollback on error, which reverts your infrastructure to its last known stable state if an update fails. This makes it a reliable and secure choice for managing AWS-exclusive infrastructure, as demonstrated by organizations like Capital One and NASA JPL for mission-critical applications.

### Strategic Breakdown

CloudFormation is the ideal choice for teams fully committed to the AWS ecosystem. It excels at creating standardized, repeatable environments. For instance, you can define a complete application stack-load balancers, auto-scaling groups, EC2 instances, and RDS databases-in a single template. This template can then be reused across different environments (dev, staging, prod), ensuring consistency and reducing manual configuration errors. It's one of the most powerful **infrastructure as code examples** for AWS-centric organizations.

> **Key Insight:** CloudFormation's biggest strength is its transactional deployment model via "change sets." This allows you to preview the exact changes that will be made to your stack before execution, preventing unintended consequences and providing an audit trail for infrastructure modifications.

### Actionable Takeaways

* **Use Nested Stacks:** For large, complex deployments, break your infrastructure into smaller, logical, and reusable templates using nested stacks. This improves maintainability and allows different teams to own different parts of the architecture.
* **Leverage Change Sets:** Never apply a template update directly. Always create and review a change set first. This provides a clear "what-if" analysis, showing you precisely which resources will be created, updated, or deleted.
* **Parameterize Your Templates:** Use parameters and mappings to make your templates flexible and reusable across different accounts or regions. This avoids hardcoding values like VPC IDs or instance sizes, making your templates more dynamic.

## 3. Ansible: The Agentless Automation Engine

Ansible is an open-source automation tool that excels at configuration management, application deployment, and orchestration. Unlike many tools that require agents on managed nodes, Ansible is agentless, communicating over standard SSH or WinRM protocols. It uses human-readable YAML files, called "playbooks," to describe automation jobs, making it highly accessible for teams of varying skill levels.

While often categorized primarily as a configuration management tool, Ansible's vast library of modules makes it a powerful force for provisioning infrastructure. Companies like NASA and ING Bank use it to manage complex, multi-tiered environments. This dual capability allows teams to use a single tool for both setting up servers and configuring the software that runs on them, streamlining the entire deployment pipeline.

### Strategic Breakdown

Ansible shines in hybrid environments where both new infrastructure provisioning and existing system configuration are required. For example, a team can use Ansible to provision a fleet of virtual machines on AWS, and then immediately use the same playbook to install web servers, configure firewall rules, and deploy an application. This seamless transition from provisioning to configuration is a key differentiator among **infrastructure as code examples**.

> **Key Insight:** Ansible's agentless architecture and simple YAML syntax lower the barrier to entry for automation. This allows operations teams, developers, and network engineers to collaborate on a single, readable automation platform, reducing complexity and increasing speed.

### Actionable Takeaways

* **Organize with Roles:** Use Ansible Roles to create reusable, self-contained units of automation. This modular approach makes your playbooks cleaner, easier to manage, and shareable across different projects and teams.
* **Secure Secrets with Vault:** Never store sensitive data like passwords or API keys in plain text. Use Ansible Vault to encrypt these variables directly within your project, ensuring they remain secure both at rest and in version control.
* **Leverage Dynamic Inventories:** For cloud environments where infrastructure is ephemeral, manually managing inventory files is impractical. Configure dynamic inventories to automatically pull host information directly from cloud providers like AWS, Azure, or Google Cloud.

## 4. Pulumi: Infrastructure as Real Code

Pulumi is a modern, open-source IaC platform that empowers developers to define and manage cloud infrastructure using familiar programming languages. Instead of a domain-specific language, teams can leverage Python, TypeScript, Go, C#, or Java to provision resources. This approach allows for the use of powerful programming constructs like loops, functions, classes, and conditionals directly in infrastructure definitions.

This makes Pulumi a compelling choice for development teams who want to apply software engineering best practices to their infrastructure management. Companies like Snowflake and Mercedes-Benz use Pulumi to streamline multi-cloud deployments and cloud-native application infrastructure, treating their infrastructure with the same rigor as their application code.

![Pulumi](https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts/infrastructure-as-code-examples/482513d1-eecc-477a-940a-41a69c4954f8.jpg)

### Strategic Breakdown

Pulumi excels where infrastructure logic becomes complex and dynamic. For instance, creating a variable number of S3 buckets based on a list of team names or dynamically configuring IAM policies based on application logic is straightforward with a general-purpose language. This makes it a highly effective choice among **infrastructure as code examples** for building sophisticated, logic-driven cloud environments.

> **Key Insight:** Pulumi's core advantage is bridging the gap between application and infrastructure code. It allows teams to use a single toolchain, language, and set of engineering practices (like unit testing and package management) for both, leading to tighter integration and faster development cycles.

### Actionable Takeaways

* **Choose Your Team's Language:** Select the programming language your team is already proficient in. This significantly lowers the barrier to entry and allows developers to become productive with IaC almost immediately.
* **Leverage Existing Ecosystems:** Use your language's package manager (e.g., npm, pip, NuGet) to manage dependencies and share reusable infrastructure components. This integrates seamlessly into existing development workflows.
* **Test Your Infrastructure:** Write unit and integration tests for your infrastructure code just as you would for application code. Pulumi's testing framework helps validate configurations before deployment, catching errors early and increasing reliability.

## 5. Azure Resource Manager (ARM) Templates

Azure Resource Manager (ARM) templates are the native Infrastructure as Code (IaC) solution for Microsoft Azure. These templates use a declarative JSON syntax to define the Azure resources you want to deploy, their configurations, and their dependencies. ARM acts as the management layer for Azure, processing these templates to create, update, or delete resources in a consistent and repeatable manner.

This deep integration with the Azure platform is ARM's core advantage. It provides immediate support for new Azure services and features, ensuring you can always manage the latest offerings. Companies like H&R Block and Progressive Insurance leverage ARM templates to enforce standardization across their Azure environments, guaranteeing that every deployment adheres to corporate policies and architectural best practices.

### Strategic Breakdown

ARM templates excel at orchestrating complex, multi-service deployments entirely within the Azure ecosystem. For instance, you can define an entire application stack, including App Service Plans, Web Apps, SQL Databases, and the networking rules that connect them, all within a single template. This makes ARM templates a cornerstone among **infrastructure as code examples** for building and managing sophisticated, Azure-native solutions.

> **Key Insight:** ARM's greatest strength is its transactional deployment engine. It analyzes dependencies and deploys resources in parallel where possible, but it also has built-in validation and pre-flight checks that can catch errors before any resources are provisioned, increasing deployment reliability.

### Actionable Takeaways

* **Embrace Parameters and Variables:** Make your templates reusable and flexible by externalizing environment-specific values into a separate parameters file. Use variables for values that are repeated within a template to simplify maintenance.
* **Use Linked Templates:** For large or complex deployments, break your main ARM template into smaller, more manageable linked templates. This modular approach improves readability, reusability, and simplifies team collaboration.
* **Leverage CI/CD Integration:** Integrate ARM template deployments into Azure DevOps Pipelines or GitHub Actions. This automates the provisioning process, enables environment promotion (dev, test, prod), and provides a full audit trail for all infrastructure changes.

## 6. Google Cloud Deployment Manager

Google Cloud Deployment Manager is Google's native Infrastructure as Code (IaC) service, allowing teams to specify, deploy, and manage Google Cloud Platform (GCP) resources declaratively. It uses simple YAML for configuration, but its true power is unlocked with Python or Jinja2 templates, enabling dynamic and programmatic infrastructure creation. This service is deeply integrated into the GCP ecosystem, providing first-party support for new services and features.

Unlike cloud-agnostic tools, Deployment Manager is purpose-built for GCP, offering day-one support for new and beta services without waiting for a third-party provider to be updated. It handles resource dependencies automatically, orchestrating the creation, update, and deletion of resources in the correct order. Companies like Bloomberg and BNY Mellon leverage it for managing complex data platforms and financial services infrastructure directly within the GCP environment.

### Strategic Breakdown

Deployment Manager excels at automating complex, GCP-native architectures. Its ability to use Python templates allows for sophisticated logic, loops, and conditionals that are difficult to replicate in purely declarative languages. This makes it a compelling choice among **infrastructure as code examples** for organizations that are fully committed to Google Cloud and need to build dynamic, reusable, and highly customized deployments.

> **Key Insight:** The use of Python and Jinja2 templates elevates Deployment Manager from a simple declarative tool to a powerful infrastructure-as-code programming framework. This allows you to treat infrastructure definitions like application code, with reusable functions, libraries, and complex logic.

### Actionable Takeaways

* **Leverage Python Templates for Logic:** For anything beyond simple resource definitions, use Python templates. This allows you to dynamically generate configurations based on environment variables, external data sources, or complex conditional logic.
* **Use Composite Types for Reusability:** Create composite types, which are essentially reusable modules or blueprints for a set of related resources. This helps you build a library of standard architectural patterns (like a web server stack) that can be deployed consistently.
* **Always Preview Changes:** Before committing any changes, use the `preview` feature (`gcloud deployment-manager deployments update my-deployment --preview`). This provides a detailed summary of what resources will be created, modified, or deleted, preventing costly mistakes.

## 7. Kubernetes YAML Manifests

Kubernetes YAML manifests are declarative configuration files that define the desired state of resources within a Kubernetes cluster. While often seen as application-layer configuration, they function as a crucial form of Infrastructure as Code for the container orchestration world. These manifests specify everything from pods and deployments to services and ingresses, enabling version-controlled and reproducible application environments.

![Kubernetes YAML Manifests](https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts/infrastructure-as-code-examples/a385fbea-e9b4-438f-9d55-b9db5c0645c6.jpg)

Pioneered by Google and now managed by the Cloud Native Computing Foundation, Kubernetes has become the standard for container orchestration. Companies like Shopify and Spotify use YAML manifests extensively to manage their complex microservices architectures. This approach treats the application's runtime environment as code, which can be stored in Git, reviewed, and deployed automatically, forming the foundation of GitOps workflows.

### Strategic Breakdown

Kubernetes YAML excels at defining the desired state of application components within a pre-existing cluster. For instance, a single set of manifest files can define a web application's deployment, specifying the container image, number of replicas, and resource requests. It can also define the service that exposes the application to other parts of the cluster and the ingress rule that makes it accessible to the outside world. This makes it one of the most powerful **infrastructure as code examples** for modern, cloud-native application delivery.

> **Key Insight:** The power of Kubernetes manifests lies in their declarative nature and the reconciliation loop. You define the "what" (e.g., three running pods of my app), and the Kubernetes control plane continuously works to make the cluster's actual state match your declared state, providing self-healing capabilities.

### Actionable Takeaways

* **Implement GitOps:** Store your YAML manifests in a Git repository and use a tool like Argo CD or Flux to automatically sync the cluster state with the repository. This creates a fully auditable and automated deployment pipeline.
* **Use Templating Tools:** For managing different environments (dev, staging, prod), raw YAML can become repetitive. Use tools like Kustomize or Helm to template your manifests, allowing you to manage environment-specific configurations without duplicating code.
* **Validate Before Applying:** Always use the `kubectl apply --dry-run=server -f .` command to validate your manifests against the Kubernetes API server. This catches syntax errors and invalid configurations before they can impact your running cluster.

## 8. Chef Infra: The Automation Cookbook

Chef Infra is a powerful automation platform that transforms infrastructure into code. It uses a pure-Ruby domain-specific language (DSL) to write "recipes" that specify the desired configuration of your systems. These recipes are grouped into "cookbooks," which the Chef client on each node pulls from a central Chef Server to configure itself, ensuring systems converge to a desired state.

This pull-based, client-server model is ideal for managing the configuration of large fleets of servers, from on-premise data centers to cloud instances. Organizations like Facebook and Nordstrom have used Chef to automate configuration management at immense scale, ensuring consistency and compliance across tens of thousands of machines. Chef's procedural approach provides granular control over the configuration process.

### Strategic Breakdown

Chef Infra excels at configuration management, particularly in complex, mutable environments where server states drift over time. For instance, a cookbook can define everything a web server needs: install Apache, configure its virtual hosts, set file permissions, and ensure the service is running. This makes it a great choice among **infrastructure as code examples** for maintaining the long-term health and consistency of existing servers.

> **Key Insight:** Chef's strength lies in its procedural nature and idempotent "resources." It allows you to define not just the end state but the step-by-step logic to get there, while ensuring that running a recipe multiple times produces the same result without unwanted changes.

### Actionable Takeaways

* **Test with Test Kitchen:** Use Test Kitchen to develop and test your cookbooks in isolated environments before deploying them to production. This significantly reduces the risk of introducing configuration errors.
* **Leverage Community Cookbooks:** The Chef Supermarket offers a vast repository of pre-built cookbooks. Use them as a starting point, but wrap or customize them to fit your organization's specific needs and security policies.
* **Integrate Compliance with InSpec:** Use Chef InSpec, a companion testing framework, to write automated tests for security and compliance. This allows you to codify your compliance rules and validate that your infrastructure adheres to them continuously.


## IaC Tools Feature Comparison

| Tool | Implementation Complexity | Resource Requirements | Expected Outcomes | Ideal Use Cases | Key Advantages |
|---------------------------|----------------------------------|-------------------------------------------|------------------------------------------------|--------------------------------------------|-----------------------------------------------------|
| Terraform | Moderate; requires learning HCL | State file management; remote backend recommended | Multi-cloud, consistent, reusable infrastructure | Multi-cloud provisioning and management | Cloud-agnostic, modular, strong plan preview |
| AWS CloudFormation | Moderate to high; verbose templates | AWS-only; uses AWS resources natively | Reliable AWS resource provisioning with rollback | AWS native infrastructure deployments | Deep AWS integration, automatic dependency and rollback |
| Ansible | Low to moderate; YAML playbooks | Agentless; SSH access to target nodes | Configuration management and cloud provisioning | Automation of configuration and provisioning | Simple YAML, no agents, built-in secrets management |
| Pulumi | Moderate to high; programming languages | Programming knowledge needed; state management | Programmable IaC with testing and multi-cloud support | Developers preferring code-centric IaC | Supports familiar languages, IDE integration, testing |
| Azure Resource Manager | Moderate to high; JSON templates | Azure resources only | Consistent Azure resource deployment | Azure native infrastructure provisioning | Native Azure integration, validation, versioning |
| Google Cloud Deployment Manager | Moderate; YAML/Python/Jinja2 | GCP resources only | Managed Google Cloud infrastructure | GCP-native infrastructure automation | Python scripting, deployment preview, dependency management |
| Kubernetes YAML Manifests | Low; declarative YAML syntax | Kubernetes cluster access | Kubernetes resource configuration and deployment | Container orchestration and app deployments | Simple YAML, native K8s approach, wide tool support |
| Chef Infra | High; Ruby DSL and agent setup | Agent installation on target nodes | Complex system configuration management | Enterprise config management, compliance | Powerful DSL, strong testing and compliance tools |


## Choosing Your IaC Tool: A Strategic Summary

Transitioning from manual infrastructure management to a code-driven methodology is a foundational shift in modern IT operations. As we've explored through a diverse set of **infrastructure as code examples**, the "best" tool is not a one-size-fits-all answer. Instead, the optimal choice depends entirely on your specific organizational context, existing technical stack, and long-term strategic goals.

The examples in this article, from Terraform's multi-cloud provisioning to the deep ecosystem integration of AWS CloudFormation and Azure ARM Templates, illustrate a critical principle: your tool selection directly influences your operational agility and architectural possibilities. Making an informed decision requires looking beyond syntax and focusing on the strategic implications.

### Synthesizing the Key Takeaways

To navigate this landscape effectively, consider the core lessons drawn from our analysis of each tool:

* **Declarative vs. Imperative:** Most modern tools, like Terraform and CloudFormation, favor a declarative approach where you define the desired end state. This simplifies management and reduces configuration drift. Imperative tools like Ansible scripts, while powerful for configuration, require you to define the step-by-step process, which can be more complex to manage at scale for provisioning.
* **Cloud-Agnostic vs. Cloud-Native:** A primary decision point is whether to commit to a single cloud provider. Tools like Terraform and Pulumi offer the strategic advantage of portability, allowing you to deploy resources across AWS, Azure, and GCP with a unified workflow. In contrast, native tools like CloudFormation offer unparalleled access to the latest services and features within their specific ecosystem, often on day one of an API release.
* **Provisioning vs. Configuration Management:** The line between these two functions is often blurred. Tools like Terraform and ARM are masters of provisioning-creating VMs, databases, and networks. Conversely, Ansible and Chef excel at configuration management-installing software, managing files, and configuring services on those provisioned resources. A robust IaC strategy often involves using both types of tools in tandem.

### Actionable Next Steps for Your IaC Journey

Understanding these concepts is the first step; applying them is what drives transformation. The practical **infrastructure as code examples** provided serve as a launchpad for your own initiatives.

1. **Evaluate Your Team's Skill Set:** Does your team primarily consist of operations engineers comfortable with HCL or JSON, or are they developers who would prefer using a general-purpose language like Python or TypeScript with Pulumi? Aligning the tool with existing expertise accelerates adoption.
2. **Start with a Small, Non-Critical Project:** Before attempting to codify your entire production environment, pick a contained project. This could be a development environment, a static website, or a single microservice. This approach allows your team to learn, make mistakes, and build confidence in a low-risk setting.
3. **Establish a "Source of Truth" Mindset:** The core value of IaC is having your infrastructure's definition stored in a version control system like Git. Enforce a strict policy where all changes are made via code commits, pull requests, and automated pipelines. This creates an auditable, repeatable, and transparent process that eliminates manual, un-tracked modifications. Mastering this discipline is the key to unlocking the full potential of automated infrastructure management.

By moving from theory to practice, you transform abstract code into a resilient, scalable, and predictable foundation for your applications. This strategic adoption of IaC is no longer just a best practice; it is a competitive necessity for any organization looking to innovate and scale effectively in the cloud.

---

Ready to implement a robust IaC strategy but need expert guidance to accelerate your journey? The team at **Pratt Solutions** specializes in crafting and implementing bespoke automation and cloud infrastructure solutions. [Pratt Solutions](https://john-pratt.com) can help you translate these examples into a production-ready system tailored to your unique business needs.
