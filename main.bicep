// ============================================================================
// WorkflowAI – Azure Landing Zone (No‑Redis Variant) – fixed commas
// ----------------------------------------------------------------------------
@description('Globally unique prefix for all resources')
param prefix string = 'wfai'

@description('Azure region')
param location string = resourceGroup().location

@description('Container image tag to deploy (e.g. "main" or a SHA)')
param imageTag string

@description('Git branch for Static Web Apps build')
param staticWebBranch string = 'main'

@secure()
@description('Cosmos admin password (Mongo)')
param cosmosPassword string

@secure()
@description('32‑byte base64 AES key for encrypted storage')
param storageAES string

@secure()
@description('32‑byte base64 HMAC key for encrypted storage')
param storageHMAC string

var acrName     = toLower('${prefix}acr')
var kvName      = toLower('${prefix}kv')
var storageName = toLower(replace('${prefix}store','-',''))
var cosmosName  = toLower('${prefix}cosmos')
var logName     = toLower('${prefix}logs')
var caeName     = toLower('${prefix}cae')
var apiAppName  = toLower('${prefix}-api')
var swaName     = toLower('${prefix}-swa')

resource acr 'Microsoft.ContainerRegistry/registries@2023-05-01-preview' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/taskruns'
  properties: {
    publicAccess: 'None'
  }
  dependsOn: [storage]
}

resource kv 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: kvName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    publicNetworkAccess: 'Enabled'
    enableSoftDelete: true
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

var blobKey  = listKeys(storage.id, '2023-05-01').keys[0].value
var blobConn = 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${blobKey};EndpointSuffix=core.windows.net'
var mongoConn = 'mongodb://admin:${uriComponent(cosmosPassword)}@${cosmosName}.mongo.cosmos.azure.com:10255/?ssl=true'

resource kvSecretMongo 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  name: '${kv.name}/mongoConn'
  properties: {
    value: mongoConn
  }
}

resource kvSecretBlob 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  name: '${kv.name}/blobConn'
  properties: {
    value: blobConn
  }
}

resource kvSecretAES 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  name: '${kv.name}/aesKey'
  properties: {
    value: storageAES
  }
}

resource kvSecretHMAC 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  name: '${kv.name}/hmacKey'
  properties: {
    value: storageHMAC
  }
}

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: cosmosName
  location: location
  kind: 'MongoDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    apiProperties: {
      serverVersion: '5.0'
    }
    enableFreeTier: true
  }
}

resource law 'Microsoft.OperationalInsights/workspaces@2023-10-01' = {
  name: logName
  location: location
  sku: {
    name: 'PerGB2018'
  }
  properties: {
    retentionInDays: 30
  }
}

resource cae 'Microsoft.App/managedEnvironments@2023-05-02-preview' = {
  name: caeName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: law.properties.customerId
        sharedKey: law.listKeys().primarySharedKey
      }
    }
    workloadProfiles: [
      {
        name: 'consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

var acrPwd = acr.listCredentials().passwords[0].value

resource apiApp 'Microsoft.App/containerApps@2023-05-02-preview' = {
  name: apiAppName
  location: location
  properties: {
    managedEnvironmentId: cae.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
      }
      registries: [
        {
          server: acr.properties.loginServer
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-pwd'
        }
      ]
      secrets: [
        {
          name: 'acr-pwd'
          value: acrPwd
        }
        {
          name: 'mongoConn'
          keyVaultUrl: reference('${kv.id}/secrets/mongoConn', '2023-02-01').secretUriWithVersion
        }
        {
          name: 'blobConn'
          keyVaultUrl: reference('${kv.id}/secrets/blobConn', '2023-02-01').secretUriWithVersion
        }
        {
          name: 'aesKey'
          keyVaultUrl: reference('${kv.id}/secrets/aesKey', '2023-02-01').secretUriWithVersion
        }
        {
          name: 'hmacKey'
          keyVaultUrl: reference('${kv.id}/secrets/hmacKey', '2023-02-01').secretUriWithVersion
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: '${acr.properties.loginServer}/workflowai-api:${imageTag}'
          env: [
            {
              name: 'WORKFLOWAI_MONGO_CONNECTION_STRING'
              secretRef: 'mongoConn'
            }
            {
              name: 'JOBS_BROKER_URL'
              value: 'memory://'
            }
            {
              name: 'WORKFLOWAI_STORAGE_CONNECTION_STRING'
              secretRef: 'blobConn'
            }
            {
              name: 'STORAGE_AES'
              secretRef: 'aesKey'
            }
            {
              name: 'STORAGE_HMAC'
              secretRef: 'hmacKey'
            }
            {
              name: 'WORKFLOWAI_ALLOWED_ORIGINS'
              value: '*'
            }
          ]
        }
        {
          name: 'worker'
          image: '${acr.properties.loginServer}/workflowai-api:${imageTag}'
          command: [
            'poetry'
            'run'
            'taskiq'
            'worker'
            'api.broker:broker'
            '--fs-discover'
            '--tasks-pattern'
            'api/jobs/*_jobs.py'
            '--workers'
            '1'
          ]
          env: [
            {
              name: 'WORKFLOWAI_MONGO_CONNECTION_STRING'
              secretRef: 'mongoConn'
            }
            {
              name: 'JOBS_BROKER_URL'
              value: 'memory://'
            }
            {
              name: 'WORKFLOWAI_STORAGE_CONNECTION_STRING'
              secretRef: 'blobConn'
            }
            {
              name: 'STORAGE_AES'
              secretRef: 'aesKey'
            }
            {
              name: 'STORAGE_HMAC'
              secretRef: 'hmacKey'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
      }
    }
  }
}

resource swa 'Microsoft.Web/staticSites@2022-09-15' = {
  name: swaName
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    repositoryUrl: 'https://github.com/kalo4ever/WorkflowAI'
    branch: staticWebBranch
    buildProperties: {
      appLocation: 'client'
      outputLocation: 'client/out'
    }
  }
}

output apiUrl string = apiApp.properties.configuration.ingress.fqdn
output staticWebUrl string = swa.properties.defaultHostname
