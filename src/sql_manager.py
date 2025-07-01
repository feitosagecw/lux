import os
from pathlib import Path

class SQLManager:
    def __init__(self):
        self.sql_dir = Path(__file__).parent / 'sql'
    
    def read_sql_file(self, filename):
        """Lê um arquivo SQL e retorna seu conteúdo."""
        file_path = self.sql_dir / filename
        with open(file_path, 'r') as file:
            return file.read()
    
    def get_user_info_sql(self, id_client):
        """Retorna a consulta SQL para informações do usuário com o ID do cliente substituído."""
        query = self.read_sql_file('user_info.sql')
        return query.format(id_client=id_client)
    
    def get_pix_concentration_sql(self, id_client):
        """Retorna a consulta SQL para concentração PIX com o ID do cliente substituído."""
        query = self.read_sql_file('pix_concentration.sql')
        return query.format(id_client=id_client)
    
    def get_card_transactions_sql(self, id_client):
        """Retorna a consulta SQL para transações de cartões com o ID do cliente substituído."""
        query = self.read_sql_file('card_transactions.sql')
        return query.format(id_client=id_client)
    
    def get_contact_info_sql(self, id_client):
        """Retorna a consulta SQL para informações de contato com o ID do cliente substituído."""
        query = self.read_sql_file('contact_info.sql')
        return query.format(id_client=id_client)
    
    def get_pep_sql(self, id_client):
        """Retorna a consulta SQL para transações PEP com o ID do cliente substituído."""
        query = self.read_sql_file('pep_transactions.sql')
        return query.format(id_client=id_client)
    
    def get_corporate_cards_sql(self, id_client):
        """Retorna a consulta SQL para cartões corporativos com o ID do cliente substituído."""
        query = self.read_sql_file('corporate_cards.sql')
        return query.format(id_client=id_client)
    
    def get_gafi_sql(self, id_client):
        """Retorna a consulta SQL para transações GAFI com o ID do cliente substituído."""
        query = self.read_sql_file('gafi_transactions.sql')
        return query.format(id_client=id_client)
    
    def get_ted_sql(self, id_client):
        """Retorna a consulta SQL para transações TED com o ID do cliente substituído."""
        query = self.read_sql_file('ted_transactions.sql')
        return query.format(id_client=id_client)
    
    def get_issuing_sql(self, id_client):
        """Retorna a consulta SQL para transações Issuing com o ID do cliente substituído."""
        query = self.read_sql_file('issuing_transactions.sql')
        return query.format(id_client=id_client)
    
    def get_acquiring_sql(self, id_client):
        """Retorna a consulta SQL para transações Acquiring com o ID do cliente substituído."""
        query = self.read_sql_file('acquiring_transactions.sql')
        return query.format(id_client=id_client)
    
    def get_card_transactions_all_sql(self):
        """Retorna a consulta SQL para todas as transações de cartões."""
        return self.read_sql_file('card_transactions_all.sql')
    
    def get_international_transactions_sql(self, id_client):
        """Retorna a consulta SQL para transações internacionais."""
        return self.read_sql_file('international_transactions.sql').format(id_client=id_client)
    
    def get_offense_analysis_sql(self, id_client):
        """Retorna a consulta SQL para análise de ofensas com o ID do cliente substituído."""
        return self.read_sql_file('offense_analysis.sql').format(id_client=id_client) 