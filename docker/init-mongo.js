// MongoDB initialization script
// This script runs when MongoDB container starts for the first time

// Switch to the speecher database
db = db.getSiblingDB('speecher');

// Create a user for the application
db.createUser({
  user: 'speecher_user',
  pwd: 'speecher_pass',
  roles: [
    {
      role: 'readWrite',
      db: 'speecher'
    }
  ]
});

// Create collections with validation
db.createCollection('transcriptions', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['filename', 'provider', 'language', 'transcript', 'created_at'],
      properties: {
        filename: {
          bsonType: 'string',
          description: 'Name of the audio file'
        },
        provider: {
          enum: ['aws', 'azure', 'gcp'],
          description: 'Cloud provider used for transcription'
        },
        language: {
          bsonType: 'string',
          description: 'Language code (e.g., en-US, pl-PL)'
        },
        transcript: {
          bsonType: 'string',
          description: 'The transcribed text'
        },
        speakers: {
          bsonType: 'array',
          description: 'Array of speaker segments'
        },
        duration: {
          bsonType: 'double',
          minimum: 0,
          description: 'Duration of audio in seconds'
        },
        cost_estimate: {
          bsonType: 'double',
          minimum: 0,
          description: 'Estimated cost of transcription'
        },
        created_at: {
          bsonType: 'date',
          description: 'Timestamp of transcription creation'
        }
      }
    }
  }
});

// Create API keys collection
db.createCollection('api_keys', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['provider', 'keys', 'enabled'],
      properties: {
        provider: {
          enum: ['aws', 'azure', 'gcp'],
          description: 'Cloud provider name'
        },
        keys: {
          bsonType: 'object',
          description: 'Encrypted API keys and configuration'
        },
        enabled: {
          bsonType: 'bool',
          description: 'Whether this provider is enabled'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Last update timestamp'
        }
      }
    }
  }
});

// Create indexes for better performance
db.transcriptions.createIndex({ created_at: -1 });
db.transcriptions.createIndex({ provider: 1 });
db.transcriptions.createIndex({ filename: 'text' });
db.api_keys.createIndex({ provider: 1 }, { unique: true });

// Create test database for integration tests
testDb = db.getSiblingDB('speecher_test');

testDb.createUser({
  user: 'speecher_user',
  pwd: 'speecher_pass',
  roles: [
    {
      role: 'readWrite',
      db: 'speecher_test'
    }
  ]
});

print('MongoDB initialization completed successfully');